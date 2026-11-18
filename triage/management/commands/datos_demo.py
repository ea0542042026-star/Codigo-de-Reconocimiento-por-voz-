"""Crea pacientes y evaluaciones de ejemplo (datos ficticios) para presentar el sistema.

Uso:  python manage.py datos_demo
"""
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from triage.models import Paciente, RegistroTriage
from triage.services.clasificador_triage import ClasificadorTriage

PACIENTES = [
    ('Ana', 'Torres', 28, 'F'), ('María', 'López', 34, 'F'), ('Juan', 'Pérez', 56, 'M'),
    ('Carlos', 'Gómez', 41, 'M'), ('Lucía', 'Fernández', 23, 'F'), ('José', 'Martínez', 67, 'M'),
    ('Sofía', 'Hernández', 8, 'F'), ('Pedro', 'Ramírez', 45, 'M'), ('Carmen', 'Flores', 72, 'F'),
    ('Luis', 'Castillo', 19, 'M'),
]

CASOS = [
    # (motivo, texto dictado, signos vitales)
    ('Dolor de pecho', 'Tengo dolor en el pecho desde hace una hora y me falta el aire',
     {'presion_sistolica': 165, 'presion_diastolica': 100, 'frecuencia_cardiaca': 118, 'saturacion': 91, 'dolor': 9}),
    ('Fiebre y vómitos', 'Mi hija tiene fiebre desde ayer y ha estado vomitando',
     {'temperatura': 38.9, 'frecuencia_cardiaca': 110, 'dolor': 4}),
    ('Tos y gripe', 'Tengo tos y gripe desde hace tres días, me duele la garganta',
     {'temperatura': 37.2, 'saturacion': 98, 'dolor': 2}),
    ('Golpe en el brazo', 'Me caí de la moto y creo que tengo una fractura en el brazo',
     {'presion_sistolica': 130, 'presion_diastolica': 85, 'dolor': 7}),
    ('Dolor de estómago', 'Tengo dolor de estómago fuerte y diarrea',
     {'temperatura': 37.8, 'dolor': 6}),
    ('Dolor de cabeza', 'Me duele la cabeza desde la mañana',
     {'presion_sistolica': 125, 'presion_diastolica': 80, 'dolor': 3}),
    ('Desmayo', 'Se desmayó en la casa y no responde bien',
     {'presion_sistolica': 85, 'presion_diastolica': 50, 'saturacion': 89}),
    ('Herida en la mano', 'Me hice una cortada en la mano con un cuchillo',
     {'dolor': 5}),
    ('Dolor de espalda', 'Tengo dolor de espalda desde hace una semana', {'dolor': 3}),
    ('Mareo', 'Me siento mareada y con dolor de cabeza fuerte',
     {'presion_sistolica': 150, 'presion_diastolica': 95}),
]


# Estado de cada caso (en el mismo orden)
ESTADOS = ['ESPERA', 'ATENCION', 'ATENDIDO', 'ESPERA', 'ESPERA',
           'ATENDIDO', 'ESPERA', 'ATENCION', 'ATENDIDO', 'ESPERA']


class Command(BaseCommand):
    help = 'Crea datos de ejemplo (ficticios) para presentar el sistema'

    def handle(self, *args, **opciones):
        random.seed(7)
        clasificador = ClasificadorTriage()
        ahora = timezone.now()
        creados = 0

        for i, (nombres, apellidos, edad, sexo) in enumerate(PACIENTES):
            paciente, _ = Paciente.objects.get_or_create(
                nombres=nombres, apellidos=apellidos,
                defaults={'edad': edad, 'sexo': sexo, 'telefono': f'7{random.randint(100, 999)}-{random.randint(1000, 9999)}'})

            motivo, texto, vitales = CASOS[i]
            resultado = clasificador.clasificar({'motivo': motivo, 'transcripcion': texto, **vitales})
            registro = RegistroTriage.objects.create(
                paciente=paciente, motivo=motivo, transcripcion=texto, **vitales,
                sintomas=', '.join(resultado.sintomas),
                razones='\n'.join(resultado.razones),
                prioridad_sugerida=resultado.prioridad,
                prioridad=resultado.prioridad,
                estado=ESTADOS[i],
            )
            # Repartir las fechas en los últimos días para que se vea la gráfica
            registro.fecha = ahora - timedelta(days=i % 7, hours=random.randint(0, 5))
            registro.save(update_fields=['fecha'])
            creados += 1

        self.stdout.write(self.style.SUCCESS(f'Listo: {creados} evaluaciones de ejemplo creadas.'))
