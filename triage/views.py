import csv
import os
from collections import Counter
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.db.models import Case, IntegerField, Q, Value, When
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import ElegirPacienteForm, PacienteForm, RegistroTriageForm
from .models import Paciente, RegistroTriage
from .services.clasificador_triage import ClasificadorTriage
from .services.servicio_transcripcion import ServicioTranscripcion, TranscripcionError
from .services.transcriptor_whisper import TranscriptorWhisper

# Reglas del audio (T012)
EXT_PERMITIDAS = {'.wav', '.mp3', '.webm', '.m4a', '.ogg'}
MAX_MB = 25

# Para ordenar la cola: primero ROJO, luego AMARILLO y al final VERDE
ORDEN_PRIORIDAD = Case(
    When(prioridad='ROJO', then=Value(1)),
    When(prioridad='AMARILLO', then=Value(2)),
    default=Value(3),
    output_field=IntegerField(),
)


def contar_prioridades(registros):
    """Cuenta cuántos registros hay de cada color."""
    return {
        'ROJO': registros.filter(prioridad='ROJO').count(),
        'AMARILLO': registros.filter(prioridad='AMARILLO').count(),
        'VERDE': registros.filter(prioridad='VERDE').count(),
    }


# =========================================================
# 1. PANEL DE INICIO
# =========================================================
@login_required
def inicio(request):
    """Muestra el panel con los números reales de la base de datos."""
    hoy = timezone.localdate()
    hace_7_dias = timezone.now() - timedelta(days=7)
    registros = RegistroTriage.objects.select_related('paciente')
    registros_hoy = registros.filter(fecha__date=hoy)

    cola = (registros.exclude(estado='ATENDIDO')
            .annotate(orden=ORDEN_PRIORIDAD).order_by('orden', 'fecha')[:6])

    return render(request, 'triage/index.html', {
        'total_pacientes': Paciente.objects.count(),
        'pacientes_semana': Paciente.objects.filter(fecha_registro__gte=hace_7_dias).count(),
        'total_audios': registros.exclude(audio='').count(),
        'total_transcripciones': registros.exclude(transcripcion='').count(),
        'alertas': registros.filter(prioridad='ROJO').exclude(estado='ATENDIDO').count(),
        'hoy': contar_prioridades(registros_hoy),
        'cola': cola,
        'recientes': registros[:5],
    })


# =========================================================
# 2. PACIENTES
# =========================================================
@login_required
def pacientes_lista(request):
    """Lista de pacientes con buscador."""
    pacientes = Paciente.objects.all()
    buscar = request.GET.get('q', '').strip()
    if buscar:
        pacientes = pacientes.filter(
            Q(nombres__icontains=buscar) | Q(apellidos__icontains=buscar) |
            Q(telefono__icontains=buscar))
    return render(request, 'triage/pacientes/lista.html', {
        'pacientes': pacientes, 'buscar': buscar,
    })


@login_required
def paciente_nuevo(request):
    """Formulario para registrar un paciente."""
    form = PacienteForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            paciente = form.save()
            messages.success(request, f'Paciente {paciente} registrado.')
            return redirect('triage:paciente_detalle', pk=paciente.pk)
        messages.error(request, 'Revisa los datos marcados en rojo.')
    return render(request, 'triage/pacientes/form.html', {
        'form': form, 'titulo': 'Nuevo paciente',
    })


@login_required
def paciente_editar(request, pk):
    """Formulario para cambiar los datos de un paciente."""
    paciente = get_object_or_404(Paciente, pk=pk)
    form = PacienteForm(request.POST or None, instance=paciente)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f'Datos de {paciente} actualizados.')
            return redirect('triage:paciente_detalle', pk=paciente.pk)
        messages.error(request, 'Revisa los datos marcados en rojo.')
    return render(request, 'triage/pacientes/form.html', {
        'form': form, 'titulo': f'Editar a {paciente}', 'paciente': paciente,
    })


@login_required
def paciente_detalle(request, pk):
    """Datos del paciente y todas sus evaluaciones de triage."""
    paciente = get_object_or_404(Paciente, pk=pk)
    return render(request, 'triage/pacientes/detalle.html', {
        'paciente': paciente, 'registros': paciente.registros.all(),
    })


@login_required
def paciente_eliminar(request, pk):
    """Pide confirmación y borra al paciente (y sus registros)."""
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        nombre = str(paciente)
        paciente.delete()
        messages.success(request, f'Paciente {nombre} eliminado.')
        return redirect('triage:pacientes')
    return render(request, 'triage/pacientes/eliminar.html', {'paciente': paciente})


# =========================================================
# 3. AUDIO Y TRANSCRIPCIÓN (Whisper)
# =========================================================
@login_required
def pagina_audio(request):
    """Muestra la página para grabar audio."""
    return render(request, 'triage/audio.html', {'paciente_id': request.GET.get('paciente', '')})


@login_required
@require_POST
def subir_audio(request):
    """Recibe el audio, lo revisa y lo guarda en media/audios."""
    archivo = request.FILES.get('audio')

    # 1. Revisar que sí llegó un archivo
    if archivo is None:
        return JsonResponse({'ok': False, 'error': 'No se recibió audio'}, status=400)

    # 2. Revisar el formato
    ext = os.path.splitext(archivo.name)[1].lower()
    if ext not in EXT_PERMITIDAS:
        return JsonResponse({'ok': False, 'error': 'Formato no permitido'}, status=400)

    # 3. Revisar el tamaño
    if archivo.size > MAX_MB * 1024 * 1024:
        return JsonResponse({'ok': False, 'error': 'Archivo muy grande'}, status=400)

    # 4. Guardar el archivo
    ruta = default_storage.save('audios/' + archivo.name, archivo)
    return JsonResponse({'ok': True, 'ruta': ruta})


def ruta_audio_valida(ruta):
    """Solo acepta audios dentro de media/audios (evita que pidan otros archivos)."""
    return ruta.startswith('audios/') and '..' not in ruta and '\\' not in ruta


@login_required
@require_POST
def transcribir_audio(request):
    """Recibe la ruta de un audio ya guardado y devuelve el texto con Whisper."""
    ruta = request.POST.get('ruta', '')
    if not ruta_audio_valida(ruta):
        return JsonResponse({'ok': False, 'error': 'Ruta de audio no válida'}, status=400)

    ruta_completa = os.path.join(settings.MEDIA_ROOT, ruta)
    servicio = ServicioTranscripcion(TranscriptorWhisper('base'))
    try:
        texto = servicio.transcribir_audio(ruta_completa)
    except TranscripcionError as error:
        return JsonResponse({'ok': False, 'error': str(error)}, status=500)

    return JsonResponse({'ok': True, 'texto': texto})


# =========================================================
# 4. TRIAGE (formulario, análisis automático y detalle)
# =========================================================
def numero(valor):
    """Convierte el texto de un campo a número; si está vacío devuelve None."""
    try:
        return float(valor) if '.' in str(valor) else int(valor)
    except (TypeError, ValueError):
        return None


@login_required
@require_POST
def analizar_texto(request):
    """Recibe el texto y los signos vitales y devuelve la prioridad sugerida."""
    datos = {
        'motivo': request.POST.get('motivo', ''),
        'transcripcion': request.POST.get('transcripcion', ''),
    }
    for campo in ['presion_sistolica', 'frecuencia_cardiaca', 'saturacion', 'temperatura', 'dolor']:
        datos[campo] = numero(request.POST.get(campo))
    resultado = ClasificadorTriage().clasificar(datos)
    return JsonResponse({'ok': True, **resultado.como_diccionario()})


@login_required
def registro_nuevo(request):
    """Formulario de triage: elige o crea el paciente y guarda la evaluación."""
    if request.method == 'POST':
        form_elegir = ElegirPacienteForm(request.POST)
        form_registro = RegistroTriageForm(request.POST)
        form_paciente = PacienteForm(request.POST)
        audio_ruta = request.POST.get('audio_ruta', '')

        elegir_ok = form_elegir.is_valid()
        existente = form_elegir.cleaned_data.get('paciente') if elegir_ok else None
        # Si eligió un paciente registrado, no hace falta llenar los datos del paciente
        paciente_ok = existente is not None or form_paciente.is_valid()

        if elegir_ok and paciente_ok and form_registro.is_valid():
            paciente = existente or form_paciente.save()
            registro = form_registro.save(commit=False)
            registro.paciente = paciente

            # Guardar también lo que sugirió el sistema
            resultado = ClasificadorTriage().clasificar(form_registro.cleaned_data)
            registro.prioridad_sugerida = resultado.prioridad
            registro.sintomas = ', '.join(resultado.sintomas)
            registro.razones = '\n'.join(resultado.razones)

            if audio_ruta and ruta_audio_valida(audio_ruta):
                registro.audio.name = audio_ruta   # une el audio grabado con este registro
            registro.save()
            messages.success(request, f'Triage de {paciente} guardado con prioridad {registro.get_prioridad_display()}.')
            return redirect('triage:registro_detalle', pk=registro.pk)
        messages.error(request, 'Revisa los datos marcados en rojo.')
    else:
        # Puede venir de la página de audio (texto + audio) o de un paciente (?paciente=)
        form_elegir = ElegirPacienteForm(initial={'paciente': request.GET.get('paciente') or None})
        form_paciente = PacienteForm()
        form_registro = RegistroTriageForm(initial={'transcripcion': request.GET.get('texto', '')})
        audio_ruta = request.GET.get('audio', '')

    if not ruta_audio_valida(audio_ruta):
        audio_ruta = ''

    return render(request, 'triage/registro.html', {
        'form_elegir': form_elegir,
        'form_paciente': form_paciente,
        'form_registro': form_registro,
        'audio_ruta': audio_ruta,
        'MEDIA_URL': settings.MEDIA_URL,
    })


@login_required
def registro_detalle(request, pk):
    """Muestra toda la evaluación de triage de un paciente."""
    registro = get_object_or_404(RegistroTriage.objects.select_related('paciente'), pk=pk)
    return render(request, 'triage/registro_detalle.html', {
        'registro': registro, 'estados': RegistroTriage.ESTADO,
    })


@login_required
@require_POST
def registro_estado(request, pk):
    """Cambia el estado: En espera -> En atención -> Atendido."""
    registro = get_object_or_404(RegistroTriage, pk=pk)
    nuevo = request.POST.get('estado')
    if nuevo in dict(RegistroTriage.ESTADO):
        registro.estado = nuevo
        registro.save(update_fields=['estado'])
        messages.success(request, f'Estado cambiado a "{registro.get_estado_display()}".')
    # Regresa a la página donde estaba (solo si es una dirección de este mismo sitio)
    volver = request.POST.get('volver', '')
    if url_has_allowed_host_and_scheme(volver, allowed_hosts={request.get_host()}):
        return redirect(volver)
    return redirect('triage:registro_detalle', pk=pk)


# =========================================================
# 5. HISTORIAL
# =========================================================
def filtrar_registros(request):
    """Aplica el buscador y los filtros del historial (se usa también para el CSV)."""
    registros = RegistroTriage.objects.select_related('paciente')

    buscar = request.GET.get('q', '').strip()
    if buscar:
        registros = registros.filter(
            Q(paciente__nombres__icontains=buscar) |
            Q(paciente__apellidos__icontains=buscar) |
            Q(motivo__icontains=buscar) |
            Q(sintomas__icontains=buscar)
        )

    prioridad = request.GET.get('prioridad', '')
    if prioridad:
        registros = registros.filter(prioridad=prioridad)

    estado = request.GET.get('estado', '')
    if estado:
        registros = registros.filter(estado=estado)

    return registros, buscar, prioridad, estado


@login_required
def historial(request):
    """Lista los registros de triage, con buscador y filtros."""
    registros, buscar, prioridad, estado = filtrar_registros(request)
    return render(request, 'triage/historial.html', {
        'registros': registros,
        'buscar': buscar,
        'prioridad': prioridad,
        'estado': estado,
        'prioridades': RegistroTriage.PRIORIDAD,
        'estados': RegistroTriage.ESTADO,
    })


@login_required
def exportar_csv(request):
    """Descarga el historial (con los mismos filtros) como archivo CSV para Excel."""
    registros, *_ = filtrar_registros(request)
    respuesta = HttpResponse(content_type='text/csv; charset=utf-8')
    respuesta['Content-Disposition'] = 'attachment; filename="historial_triage.csv"'
    respuesta.write('﻿')  # para que Excel lea bien las tildes
    escritor = csv.writer(respuesta)
    escritor.writerow(['Fecha', 'Paciente', 'Edad', 'Motivo', 'Síntomas', 'Prioridad', 'Sugerida', 'Estado'])
    for r in registros:
        escritor.writerow([
            timezone.localtime(r.fecha).strftime('%d/%m/%Y %H:%M'), r.paciente, r.paciente.edad,
            r.motivo, r.sintomas, r.get_prioridad_display(),
            r.get_prioridad_sugerida_display(), r.get_estado_display(),
        ])
    return respuesta


# =========================================================
# 6. REPORTES
# =========================================================
@login_required
def reportes(request):
    """Números y gráficas sencillas de todos los registros."""
    registros = RegistroTriage.objects.all()
    total = registros.count()

    # Prioridades con su porcentaje
    conteo = contar_prioridades(registros)
    prioridades = [
        {'clave': clave, 'nombre': nombre, 'cantidad': conteo[clave],
         'porcentaje': round(conteo[clave] * 100 / total) if total else 0}
        for clave, nombre in RegistroTriage.PRIORIDAD
    ]

    # Registros de los últimos 7 días
    hoy = timezone.localdate()
    dias = []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        dias.append({'dia': dia, 'cantidad': registros.filter(fecha__date=dia).count()})
    maximo = max([d['cantidad'] for d in dias] + [1])
    for d in dias:
        d['alto'] = round(d['cantidad'] * 100 / maximo)

    # Síntomas más comunes
    contador = Counter()
    for texto in registros.exclude(sintomas='').values_list('sintomas', flat=True):
        contador.update(s.strip() for s in texto.split(',') if s.strip())
    top = contador.most_common(6)
    mayor = top[0][1] if top else 1
    sintomas = [{'nombre': n, 'cantidad': c, 'ancho': round(c * 100 / mayor)} for n, c in top]

    # ¿Cuántas veces el personal aceptó la sugerencia del sistema?
    con_sugerencia = registros.exclude(prioridad_sugerida='')
    coinciden = sum(1 for r in con_sugerencia if r.prioridad == r.prioridad_sugerida)

    return render(request, 'triage/reportes.html', {
        'total': total,
        'prioridades': prioridades,
        'dias': dias,
        'sintomas': sintomas,
        'estados': [(nombre, registros.filter(estado=clave).count()) for clave, nombre in RegistroTriage.ESTADO],
        'total_pacientes': Paciente.objects.count(),
        'atendidos': registros.filter(estado='ATENDIDO').count(),
        'coincidencia': round(coinciden * 100 / con_sugerencia.count()) if con_sugerencia.count() else 0,
    })
