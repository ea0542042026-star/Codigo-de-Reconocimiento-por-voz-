from abc import ABC, abstractmethod


class Transcriptor(ABC):
    """Clase abstracta: define QUÉ debe hacer cualquier transcriptor.

    No se puede usar directamente. Cada forma de pasar voz a texto
    (Whisper u otra) es una clase hija que escribe su propio transcribir().
    """

    @abstractmethod
    def transcribir(self, ruta_audio: str) -> str:
        """Recibe la ruta de un archivo de audio y devuelve el texto."""
