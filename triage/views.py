import os

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage

from .forms import PacienteForm, RegistroTriageForm
from .models import RegistroTriage
from .services.transcriptor_whisper import TranscriptorWhisper
from .services.servicio_transcripcion import ServicioTranscripcion, TranscripcionError

# Reglas del audio (T012)
EXT_PERMITIDAS = {'.wav', '.mp3', '.webm', '.m4a', '.ogg'}
MAX_MB = 25


def inicio(request):
    """Muestra el panel del administrador."""
    return render(request, 'triage/index.html')


def pagina_audio(request):
    """Muestra la página para grabar audio."""
    return render(request, 'triage/audio.html')


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


def registro_nuevo(request):
    """Muestra el formulario de triage y guarda el paciente y su evaluación."""
    if request.method == 'POST':
        form_paciente = PacienteForm(request.POST)
        form_registro = RegistroTriageForm(request.POST)
        if form_paciente.is_valid() and form_registro.is_valid():
            paciente = form_paciente.save()
            registro = form_registro.save(commit=False)
            registro.paciente = paciente
            audio_ruta = request.POST.get('audio_ruta', '')
            if audio_ruta and ruta_audio_valida(audio_ruta):
                registro.audio.name = audio_ruta   # une el audio grabado con este registro
            registro.save()
            messages.success(request, f'Registro de {paciente} guardado con éxito.')
            return redirect('triage:historial')
        messages.error(request, 'Revisa los datos marcados en rojo.')
        audio_ruta = request.POST.get('audio_ruta', '')
    else:
        # Si viene de la página de audio, llega el texto de Whisper y la ruta del audio
        form_paciente = PacienteForm()
        form_registro = RegistroTriageForm(initial={'transcripcion': request.GET.get('texto', '')})
        audio_ruta = request.GET.get('audio', '')

    if not ruta_audio_valida(audio_ruta):
        audio_ruta = ''

    return render(request, 'triage/registro.html', {
        'form_paciente': form_paciente,
        'form_registro': form_registro,
        'audio_ruta': audio_ruta,
        'MEDIA_URL': settings.MEDIA_URL,
    })


def historial(request):
    """Lista los registros de triage, con buscador y filtro por prioridad."""
    registros = RegistroTriage.objects.select_related('paciente')

    buscar = request.GET.get('q', '').strip()
    if buscar:
        registros = registros.filter(
            Q(paciente__nombres__icontains=buscar) |
            Q(paciente__apellidos__icontains=buscar) |
            Q(motivo__icontains=buscar)
        )

    prioridad = request.GET.get('prioridad', '')
    if prioridad:
        registros = registros.filter(prioridad=prioridad)

    return render(request, 'triage/historial.html', {
        'registros': registros,
        'buscar': buscar,
        'prioridad': prioridad,
        'prioridades': RegistroTriage.PRIORIDAD,
    })
