import shutil
import tempfile
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Grabacion
from .services.servicio_transcripcion import TranscripcionError

CARPETA_PRUEBA = tempfile.mkdtemp()


# Las pruebas guardan los archivos en una carpeta temporal, no en media/
@override_settings(MEDIA_ROOT=CARPETA_PRUEBA)
class GrabacionesTest(TestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(CARPETA_PRUEBA, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        User.objects.create_user('aldair', password='clave12345')
        self.client.login(username='aldair', password='clave12345')

    def subir(self, nombre='voz.webm'):
        return self.client.post(reverse('triage:subir_audio'),
                                {'audio': SimpleUploadedFile(nombre, b'audio de prueba')})

    def test_sin_sesion_manda_al_login(self):
        self.client.logout()
        respuesta = self.client.get(reverse('triage:inicio'))
        self.assertIn('/login/', respuesta.url)

    def test_paginas_abren(self):
        for nombre in ['inicio', 'grabaciones']:
            self.assertEqual(self.client.get(reverse('triage:' + nombre)).status_code, 200)

    @patch('triage.views.ServicioTranscripcion.transcribir_audio', return_value='Hola, esto es una prueba')
    def test_grabaciones_se_numeran_y_guardan_audio_y_texto(self, _):
        self.subir()
        self.subir()
        g1, g2 = Grabacion.objects.order_by('numero')
        self.assertEqual((g1.numero, g2.numero), (1, 2))
        self.assertEqual(g2.audio.name, 'reconocimiento_de_voz/grabacion_002.webm')
        self.assertEqual(g2.archivo_texto.name, 'transcripciones/grabacion_002.txt')
        with g2.archivo_texto.open('rb') as f:
            self.assertEqual(f.read().decode('utf-8'), 'Hola, esto es una prueba')

    @patch('triage.views.ServicioTranscripcion.transcribir_audio',
           side_effect=TranscripcionError('Whisper no está instalado.'))
    def test_si_whisper_falla_el_audio_igual_se_guarda(self, _):
        respuesta = self.subir().json()
        self.assertTrue(respuesta['ok'])
        self.assertEqual(respuesta['error'], 'Whisper no está instalado.')
        self.assertEqual(Grabacion.objects.get().texto, '')

    def test_formato_no_permitido(self):
        self.assertEqual(self.subir('nota.txt').status_code, 400)
        self.assertEqual(Grabacion.objects.count(), 0)

    @patch('triage.views.ServicioTranscripcion.transcribir_audio', return_value='texto con error')
    def test_corregir_texto_actualiza_el_txt(self, _):
        self.subir()
        g = Grabacion.objects.get()
        self.client.post(reverse('triage:detalle', args=[g.pk]), {'texto': 'texto corregido'})
        g.refresh_from_db()
        with g.archivo_texto.open('rb') as f:
            self.assertEqual(f.read().decode('utf-8'), 'texto corregido')

    @patch('triage.views.ServicioTranscripcion.transcribir_audio', return_value='hola')
    def test_eliminar_borra_los_archivos(self, _):
        self.subir()
        g = Grabacion.objects.get()
        audio, texto = g.audio.path, g.archivo_texto.path
        self.client.post(reverse('triage:eliminar', args=[g.pk]))
        self.assertEqual(Grabacion.objects.count(), 0)
        import os
        self.assertFalse(os.path.exists(audio) or os.path.exists(texto))
