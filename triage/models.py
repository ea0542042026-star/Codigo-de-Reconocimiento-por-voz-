from django.core.files.base import ContentFile
from django.db import models


class Grabacion(models.Model):
    """Una grabación de voz con su número y el texto que sacó Whisper."""

    numero = models.PositiveIntegerField('Número', unique=True)

    # El audio se guarda en media/reconocimiento_de_voz/
    audio = models.FileField('Audio', upload_to='reconocimiento_de_voz/')

    # El texto se guarda en la base de datos y también como archivo .txt
    # en media/transcripciones/
    texto = models.TextField('Texto', blank=True)
    archivo_texto = models.FileField('Archivo de texto', upload_to='transcripciones/', blank=True)

    error = models.CharField('Error al transcribir', max_length=300, blank=True)
    fecha = models.DateTimeField('Fecha y hora', auto_now_add=True)

    class Meta:
        verbose_name = 'Grabación'
        verbose_name_plural = 'Grabaciones'
        ordering = ['-numero']

    def __str__(self):
        return f'Grabación {self.numero}'

    @property
    def nombre_archivo(self):
        """Nombre base de los archivos: grabacion_001, grabacion_002..."""
        return f'grabacion_{self.numero:03d}'

    @staticmethod
    def siguiente_numero():
        """El número que le toca a la próxima grabación."""
        ultima = Grabacion.objects.order_by('-numero').first()
        return ultima.numero + 1 if ultima else 1

    def guardar_texto(self, texto):
        """Guarda el texto en la base de datos y lo escribe en su archivo .txt."""
        self.texto = texto.strip()
        self.error = ''
        if self.archivo_texto:
            self.archivo_texto.delete(save=False)   # borra el .txt viejo
        contenido = ContentFile(self.texto.encode('utf-8'))
        self.archivo_texto.save(self.nombre_archivo + '.txt', contenido, save=False)
        self.save()

    def borrar_archivos(self):
        """Borra el audio y el .txt de las carpetas."""
        if self.audio:
            self.audio.delete(save=False)
        if self.archivo_texto:
            self.archivo_texto.delete(save=False)
