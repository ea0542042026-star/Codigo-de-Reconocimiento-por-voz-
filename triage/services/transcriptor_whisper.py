from .transcriptor import Transcriptor


class TranscriptorWhisper(Transcriptor):
    """Hereda de Transcriptor y usa OpenAI Whisper para pasar la voz a texto."""

    # El modelo pesa mucho; se carga una sola vez y se guarda aquí
    _modelos_cargados = {}

    def __init__(self, modelo='base', idioma='es'):
        self.modelo = modelo      # tiny, base, small... (más grande = más exacto y más lento)
        self.idioma = idioma      # 'es' = español

    def _cargar_modelo(self):
        if self.modelo not in TranscriptorWhisper._modelos_cargados:
            import whisper  # se importa aquí para que Django funcione aunque Whisper no esté instalado
            TranscriptorWhisper._modelos_cargados[self.modelo] = whisper.load_model(self.modelo)
        return TranscriptorWhisper._modelos_cargados[self.modelo]

    def transcribir(self, ruta_audio):
        modelo = self._cargar_modelo()
        # fp16=False porque en una computadora sin tarjeta gráfica no se puede usar
        resultado = modelo.transcribe(str(ruta_audio), language=self.idioma, fp16=False)
        return resultado['text'].strip()
