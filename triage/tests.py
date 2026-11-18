from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Paciente, RegistroTriage
from .services.analizador_sintomas import AnalizadorSintomas
from .services.clasificador_triage import ClasificadorTriage


class AnalizadorSintomasTest(TestCase):
    """Pruebas del NLP: ¿encuentra los síntomas en el texto?"""

    def test_encuentra_dolor_de_pecho_sin_importar_tildes(self):
        nombres = [s.nombre for s in AnalizadorSintomas().analizar('Tengo DOLOR en el PÉCHO')]
        self.assertIn('Dolor de pecho', nombres)

    def test_no_confunde_tos_con_datos(self):
        nombres = [s.nombre for s in AnalizadorSintomas().analizar('Revisé los datos')]
        self.assertNotIn('Tos', nombres)


class ClasificadorTriageTest(TestCase):
    """Pruebas del clasificador: ¿sugiere el color correcto?"""

    def setUp(self):
        self.clasificador = ClasificadorTriage()

    def test_dolor_de_pecho_es_rojo(self):
        r = self.clasificador.clasificar({'motivo': 'dolor de pecho'})
        self.assertEqual(r.prioridad, 'ROJO')

    def test_fiebre_es_amarillo(self):
        r = self.clasificador.clasificar({'motivo': 'tengo fiebre'})
        self.assertEqual(r.prioridad, 'AMARILLO')

    def test_tos_es_verde(self):
        r = self.clasificador.clasificar({'motivo': 'tengo tos'})
        self.assertEqual(r.prioridad, 'VERDE')

    def test_saturacion_baja_es_rojo_aunque_el_texto_sea_leve(self):
        r = self.clasificador.clasificar({'motivo': 'tengo tos', 'saturacion': 85})
        self.assertEqual(r.prioridad, 'ROJO')

    def test_sin_datos_es_verde(self):
        self.assertEqual(self.clasificador.clasificar({}).prioridad, 'VERDE')


class PaginasTest(TestCase):
    """Pruebas de las páginas (vistas)."""

    def setUp(self):
        User.objects.create_user('enfermera', password='clave12345')
        self.client.login(username='enfermera', password='clave12345')

    def test_sin_sesion_manda_al_login(self):
        self.client.logout()
        respuesta = self.client.get(reverse('triage:inicio'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('/login/', respuesta.url)

    def test_todas_las_paginas_abren(self):
        for nombre in ['inicio', 'pacientes', 'paciente_nuevo', 'pagina_audio',
                       'registro_nuevo', 'historial', 'reportes', 'exportar_csv']:
            self.assertEqual(self.client.get(reverse('triage:' + nombre)).status_code, 200, nombre)

    def test_guardar_triage_con_paciente_nuevo(self):
        respuesta = self.client.post(reverse('triage:registro_nuevo'), {
            'nombres': 'Ana', 'apellidos': 'Torres', 'edad': 28, 'sexo': 'F',
            'motivo': 'Dolor de pecho', 'prioridad': 'ROJO',
        })
        registro = RegistroTriage.objects.get()
        self.assertRedirects(respuesta, reverse('triage:registro_detalle', args=[registro.pk]))
        self.assertEqual(registro.prioridad_sugerida, 'ROJO')
        self.assertIn('Dolor de pecho', registro.sintomas)

    def test_guardar_triage_con_paciente_registrado(self):
        paciente = Paciente.objects.create(nombres='Juan', apellidos='Pérez', edad=50, sexo='M')
        self.client.post(reverse('triage:registro_nuevo'), {
            'paciente': paciente.pk, 'motivo': 'Tos', 'prioridad': 'VERDE',
        })
        self.assertEqual(paciente.registros.count(), 1)
        self.assertEqual(Paciente.objects.count(), 1)   # no creó otro paciente

    def test_diastolica_mayor_que_sistolica_da_error(self):
        self.client.post(reverse('triage:registro_nuevo'), {
            'nombres': 'Ana', 'apellidos': 'Torres', 'edad': 28, 'sexo': 'F', 'motivo': 'Mareo',
            'presion_sistolica': 100, 'presion_diastolica': 120, 'prioridad': 'VERDE',
        })
        self.assertEqual(RegistroTriage.objects.count(), 0)

    def test_analizar_devuelve_prioridad(self):
        respuesta = self.client.post(reverse('triage:analizar_texto'), {'motivo': 'convulsiones'})
        self.assertEqual(respuesta.json()['prioridad'], 'ROJO')

    def test_cambiar_estado(self):
        paciente = Paciente.objects.create(nombres='Juan', apellidos='Pérez', edad=50, sexo='M')
        registro = RegistroTriage.objects.create(paciente=paciente, motivo='Tos')
        self.client.post(reverse('triage:registro_estado', args=[registro.pk]), {'estado': 'ATENDIDO'})
        registro.refresh_from_db()
        self.assertEqual(registro.estado, 'ATENDIDO')

    def test_subir_formato_no_permitido(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        archivo = SimpleUploadedFile('nota.txt', b'hola')
        respuesta = self.client.post(reverse('triage:subir_audio'), {'audio': archivo})
        self.assertEqual(respuesta.status_code, 400)

    def test_telefono_invalido(self):
        respuesta = self.client.post(reverse('triage:paciente_nuevo'), {
            'nombres': 'Ana', 'apellidos': 'Torres', 'edad': 28, 'sexo': 'F', 'telefono': 'abc'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Paciente.objects.count(), 0)
