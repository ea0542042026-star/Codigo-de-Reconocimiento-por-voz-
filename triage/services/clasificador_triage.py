from abc import ABC, abstractmethod

from .analizador_sintomas import AnalizadorSintomas

# Orden de gravedad: entre más alto el número, más urgente
GRAVEDAD = {'VERDE': 1, 'AMARILLO': 2, 'ROJO': 3}


class Regla(ABC):
    """Clase abstracta: cada regla revisa los datos y dice qué prioridad sugiere.

    evaluar() devuelve una lista de (prioridad, razón).
    """

    @abstractmethod
    def evaluar(self, datos):
        pass


class ReglaSintomas(Regla):
    """Revisa el texto (motivo + transcripción) con el analizador de síntomas."""

    def __init__(self):
        self.analizador = AnalizadorSintomas()

    def evaluar(self, datos):
        texto = f"{datos.get('motivo', '')} {datos.get('transcripcion', '')}"
        return [(s.nivel, f'Síntoma: {s.nombre}') for s in self.analizador.analizar(texto)]


class ReglaSignosVitales(Regla):
    """Revisa los signos vitales con límites sencillos."""

    def evaluar(self, datos):
        resultado = []
        sis = datos.get('presion_sistolica')
        fc = datos.get('frecuencia_cardiaca')
        sat = datos.get('saturacion')
        temp = datos.get('temperatura')

        if sat is not None:
            if sat < 90:
                resultado.append(('ROJO', f'Saturación muy baja ({sat}%)'))
            elif sat < 94:
                resultado.append(('AMARILLO', f'Saturación baja ({sat}%)'))

        if sis is not None:
            if sis >= 180 or sis < 90:
                resultado.append(('ROJO', f'Presión sistólica peligrosa ({sis} mmHg)'))
            elif sis >= 140:
                resultado.append(('AMARILLO', f'Presión sistólica alta ({sis} mmHg)'))

        if fc is not None:
            if fc > 130 or fc < 40:
                resultado.append(('ROJO', f'Frecuencia cardiaca peligrosa ({fc} lpm)'))
            elif fc > 100 or fc < 50:
                resultado.append(('AMARILLO', f'Frecuencia cardiaca fuera de lo normal ({fc} lpm)'))

        if temp is not None:
            temp = float(temp)
            if temp >= 40 or temp < 35:
                resultado.append(('ROJO', f'Temperatura peligrosa ({temp} °C)'))
            elif temp >= 38:
                resultado.append(('AMARILLO', f'Fiebre ({temp} °C)'))

        return resultado


class ReglaDolor(Regla):
    """Revisa la escala de dolor de 0 a 10."""

    def evaluar(self, datos):
        dolor = datos.get('dolor')
        if dolor is None:
            return []
        if dolor >= 8:
            return [('ROJO', f'Dolor muy fuerte ({dolor}/10)')]
        if dolor >= 5:
            return [('AMARILLO', f'Dolor moderado ({dolor}/10)')]
        return []


class ResultadoTriage:
    """Lo que devuelve el clasificador: prioridad, síntomas y razones."""

    def __init__(self, prioridad, sintomas, razones):
        self.prioridad = prioridad
        self.sintomas = sintomas
        self.razones = razones

    def como_diccionario(self):
        return {'prioridad': self.prioridad, 'sintomas': self.sintomas, 'razones': self.razones}


class ClasificadorTriage:
    """Junta varias reglas y elige la prioridad más grave que encuentren.

    Usa polimorfismo: no le importa qué regla es, solo llama a evaluar().
    """

    def __init__(self, reglas=None):
        self.reglas = reglas or [ReglaSintomas(), ReglaSignosVitales(), ReglaDolor()]

    def clasificar(self, datos):
        hallazgos = []
        for regla in self.reglas:
            hallazgos.extend(regla.evaluar(datos))

        if not hallazgos:
            return ResultadoTriage('VERDE', [], ['No se encontraron señales de urgencia'])

        prioridad = max((nivel for nivel, _ in hallazgos), key=lambda n: GRAVEDAD[n])
        # Primero las razones más graves
        hallazgos.sort(key=lambda h: GRAVEDAD[h[0]], reverse=True)
        razones = [razon for _, razon in hallazgos]
        sintomas = [r.replace('Síntoma: ', '') for r in razones if r.startswith('Síntoma: ')]
        return ResultadoTriage(prioridad, sintomas, razones)
