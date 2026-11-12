import os


class TranscripcionError(Exception):
    """Error con un mensaje claro para mostrar en la página."""


class ServicioTranscripcion:
    """Usa cualquier Transcriptor para obtener el texto de un audio.

    No le importa si es Whisper u otro: solo llama a transcribir().
    Eso es polimorfismo.
    """

    def __init__(self, transcriptor):
        self.transcriptor = transcriptor

    def transcribir_audio(self, ruta_audio):
        if not os.path.exists(ruta_audio):
            raise TranscripcionError('No se encontró el archivo de audio.')

        try:
            texto = self.transcriptor.transcribir(ruta_audio)
        except ImportError:
            raise TranscripcionError(
                'Whisper no está instalado. En la terminal: python -m pip install openai-whisper')
        except FileNotFoundError:
            # Whisper usa FFmpeg para leer el audio; si no está instalado sale este error
            raise TranscripcionError(
                'Falta FFmpeg. En la terminal: winget install ffmpeg (luego cierra y abre VS Code)')

        if not texto:
            raise TranscripcionError('No se entendió nada en el audio. Intenta hablar más cerca del micrófono.')
        return texto
