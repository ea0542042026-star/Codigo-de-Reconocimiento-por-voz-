from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Paciente(models.Model):
    """Datos básicos del paciente que llega a emergencias (datos ficticios)."""

    SEXO = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    nombres = models.CharField('Nombres', max_length=100)
    apellidos = models.CharField('Apellidos', max_length=100)
    edad = models.PositiveIntegerField('Edad', validators=[MaxValueValidator(120)])
    sexo = models.CharField('Sexo', max_length=1, choices=SEXO)
    telefono = models.CharField('Teléfono', max_length=15, blank=True)
    fecha_registro = models.DateTimeField('Fecha de registro', auto_now_add=True)

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f'{self.nombres} {self.apellidos}'

    def ultimo_registro(self):
        """Devuelve la evaluación de triage más reciente del paciente."""
        return self.registros.first()


class RegistroTriage(models.Model):
    """Una evaluación de triage de un paciente."""

    PRIORIDAD = [
        ('ROJO', 'Rojo - Emergencia'),
        ('AMARILLO', 'Amarillo - Urgencia'),
        ('VERDE', 'Verde - No urgente'),
    ]

    ESTADO = [
        ('ESPERA', 'En espera'),
        ('ATENCION', 'En atención'),
        ('ATENDIDO', 'Atendido'),
    ]

    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE,
        related_name='registros', verbose_name='Paciente',
    )
    motivo = models.TextField('Motivo de consulta')
    transcripcion = models.TextField('Texto dictado', blank=True)
    audio = models.FileField('Audio', upload_to='audios/', blank=True)

    # Signos vitales (pueden quedar vacíos)
    presion_sistolica = models.PositiveIntegerField(
        'Presión sistólica (mmHg)', null=True, blank=True,
        validators=[MinValueValidator(50), MaxValueValidator(250)])
    presion_diastolica = models.PositiveIntegerField(
        'Presión diastólica (mmHg)', null=True, blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(150)])
    frecuencia_cardiaca = models.PositiveIntegerField(
        'Frecuencia cardiaca (lpm)', null=True, blank=True,
        validators=[MinValueValidator(20), MaxValueValidator(250)])
    saturacion = models.PositiveIntegerField(
        'Saturación de oxígeno (%)', null=True, blank=True,
        validators=[MinValueValidator(50), MaxValueValidator(100)])
    temperatura = models.DecimalField(
        'Temperatura (°C)', max_digits=4, decimal_places=1, null=True, blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(45)])
    dolor = models.PositiveIntegerField(
        'Dolor (0 a 10)', null=True, blank=True,
        validators=[MaxValueValidator(10)])

    # Resultado del análisis automático (NLP + signos vitales)
    sintomas = models.CharField('Síntomas detectados', max_length=300, blank=True)
    razones = models.TextField('Razones de la sugerencia', blank=True)
    prioridad_sugerida = models.CharField(
        'Prioridad sugerida', max_length=10, choices=PRIORIDAD, blank=True)

    # Decisión final del personal de salud
    prioridad = models.CharField('Prioridad', max_length=10, choices=PRIORIDAD, default='VERDE')
    estado = models.CharField('Estado', max_length=10, choices=ESTADO, default='ESPERA')
    fecha = models.DateTimeField('Fecha y hora', auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de triage'
        verbose_name_plural = 'Registros de triage'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.paciente} - {self.get_prioridad_display()}'

    def lista_sintomas(self):
        """Devuelve los síntomas como lista para mostrarlos como etiquetas."""
        return [s.strip() for s in self.sintomas.split(',') if s.strip()]

    def lista_razones(self):
        return [r for r in self.razones.splitlines() if r.strip()]
