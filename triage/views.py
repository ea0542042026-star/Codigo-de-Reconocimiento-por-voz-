import os

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage

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
