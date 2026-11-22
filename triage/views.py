import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Grabacion
from .services.servicio_transcripcion import ServicioTranscripcion, TranscripcionError
from .services.transcriptor_whisper import TranscriptorWhisper

# Reglas del audio
EXT_PERMITIDAS = {'.wav', '.mp3', '.webm', '.m4a', '.ogg'}
MAX_MB = 25


def transcribir(grabacion):
    """Pasa el audio a texto con Whisper y guarda el .txt.

    Si algo falla, guarda el mensaje de error para mostrarlo en la página.
    """
    servicio = ServicioTranscripcion(TranscriptorWhisper('base'))
    try:
        texto = servicio.transcribir_audio(grabacion.audio.path)
        grabacion.guardar_texto(texto)
    except TranscripcionError as error:
        grabacion.error = str(error)
        grabacion.save(update_fields=['error'])


# =========================================================
# 1. PÁGINA PRINCIPAL: GRABAR
# =========================================================
@login_required
def inicio(request):
    """Página para grabar. Abajo muestra las últimas grabaciones."""
    return render(request, 'triage/index.html', {
        'total': Grabacion.objects.count(),
        'con_texto': Grabacion.objects.exclude(texto='').count(),
        'siguiente': Grabacion.siguiente_numero(),
        'recientes': Grabacion.objects.all()[:5],
    })


@login_required
@require_POST
def subir_audio(request):
    """Recibe el audio, lo numera, lo guarda y lo pasa a texto."""
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
        return JsonResponse({'ok': False, 'error': 'Archivo muy grande (máximo 25 MB)'}, status=400)

    # 4. Darle su número y guardarlo como grabacion_001.webm, grabacion_002.webm...
    grabacion = Grabacion(numero=Grabacion.siguiente_numero())
    grabacion.audio.save(grabacion.nombre_archivo + ext, archivo, save=False)
    grabacion.save()

    # 5. Pasarlo a texto (si Whisper falla, el audio igual queda guardado)
    transcribir(grabacion)

    return JsonResponse({
        'ok': True,
        'numero': grabacion.numero,
        'texto': grabacion.texto,
        'error': grabacion.error,
        'url': reverse('triage:detalle', args=[grabacion.pk]),
    })


# =========================================================
# 2. LISTA DE GRABACIONES
# =========================================================
@login_required
def grabaciones(request):
    """Lista numerada de todas las grabaciones, con buscador."""
    lista = Grabacion.objects.all()
    buscar = request.GET.get('q', '').strip()
    if buscar:
        filtro = Q(texto__icontains=buscar)
        if buscar.isdigit():
            filtro |= Q(numero=int(buscar))
        lista = lista.filter(filtro)
    return render(request, 'triage/grabaciones.html', {'grabaciones': lista, 'buscar': buscar})


# =========================================================
# 3. DETALLE: ESCUCHAR, VER Y CORREGIR EL TEXTO
# =========================================================
@login_required
def detalle(request, pk):
    """Muestra una grabación. Si se envía el formulario, guarda el texto corregido."""
    grabacion = get_object_or_404(Grabacion, pk=pk)
    if request.method == 'POST':
        grabacion.guardar_texto(request.POST.get('texto', ''))
        messages.success(request, f'Texto de la {grabacion} guardado.')
        return redirect('triage:detalle', pk=pk)

    # Para los botones "anterior" y "siguiente"
    anterior = Grabacion.objects.filter(numero__lt=grabacion.numero).order_by('-numero').first()
    siguiente = Grabacion.objects.filter(numero__gt=grabacion.numero).order_by('numero').first()
    return render(request, 'triage/detalle.html', {
        'g': grabacion, 'anterior': anterior, 'siguiente': siguiente,
    })


@login_required
@require_POST
def transcribir_otra_vez(request, pk):
    """Vuelve a intentar pasar el audio a texto (por si falló la primera vez)."""
    grabacion = get_object_or_404(Grabacion, pk=pk)
    transcribir(grabacion)
    if grabacion.error:
        messages.error(request, grabacion.error)
    else:
        messages.success(request, f'{grabacion} transcrita.')
    return redirect('triage:detalle', pk=pk)


@login_required
def descargar_texto(request, pk):
    """Descarga el archivo .txt de una grabación."""
    grabacion = get_object_or_404(Grabacion, pk=pk)
    if not grabacion.archivo_texto:
        raise Http404('Esta grabación todavía no tiene texto.')
    return FileResponse(grabacion.archivo_texto.open('rb'), as_attachment=True,
                        filename=grabacion.nombre_archivo + '.txt')


@login_required
def eliminar(request, pk):
    """Pide confirmación y borra la grabación con sus dos archivos."""
    grabacion = get_object_or_404(Grabacion, pk=pk)
    if request.method == 'POST':
        nombre = str(grabacion)
        grabacion.borrar_archivos()
        grabacion.delete()
        messages.success(request, f'{nombre} eliminada.')
        return redirect('triage:grabaciones')
    return render(request, 'triage/eliminar.html', {'g': grabacion})
