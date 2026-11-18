import re
import unicodedata


def normalizar(texto):
    """Pasa el texto a minúsculas y le quita las tildes.

    Así "Dolor de PECHO" y "dolor de pécho" se leen igual.
    """
    texto = unicodedata.normalize('NFD', texto.lower())
    return ''.join(letra for letra in texto if unicodedata.category(letra) != 'Mn')


class Sintoma:
    """Un síntoma que el sistema sabe reconocer en el texto."""

    def __init__(self, nombre, nivel, palabras):
        self.nombre = nombre        # cómo se muestra: "Dolor de pecho"
        self.nivel = nivel          # 'ROJO', 'AMARILLO' o 'VERDE'
        self.palabras = palabras    # frases que lo indican en el texto

    def aparece_en(self, texto_normalizado):
        # \b = inicio de palabra: así "tos" no se confunde con "datos"
        return any(re.search(r'\b' + re.escape(normalizar(p)), texto_normalizado)
                   for p in self.palabras)


class AnalizadorSintomas:
    """NLP sencillo: busca palabras clave de síntomas dentro del texto dictado."""

    SINTOMAS = [
        # Rojo: puede poner en riesgo la vida
        Sintoma('Dolor de pecho', 'ROJO', ['dolor de pecho', 'dolor en el pecho', 'opresion en el pecho', 'me duele el pecho']),
        Sintoma('Dificultad para respirar', 'ROJO', ['no puedo respirar', 'dificultad para respirar', 'me falta el aire', 'falta de aire', 'me ahogo', 'ahogo']),
        Sintoma('Pérdida de conciencia', 'ROJO', ['desmay', 'perdio el conocimiento', 'perdi el conocimiento', 'inconsciente', 'no responde']),
        Sintoma('Convulsiones', 'ROJO', ['convulsion', 'convulsiona', 'ataque epileptico']),
        Sintoma('Sangrado abundante', 'ROJO', ['sangrado abundante', 'mucha sangre', 'hemorragia', 'sangra mucho']),
        Sintoma('Señales de derrame', 'ROJO', ['no puede hablar', 'cara torcida', 'no siento un lado', 'paralisis']),
        Sintoma('Reacción alérgica grave', 'ROJO', ['se me cierra la garganta', 'se le cierra la garganta', 'hinchazon de la cara']),

        # Amarillo: necesita atención pronto
        Sintoma('Fiebre', 'AMARILLO', ['fiebre', 'calentura', 'temperatura alta']),
        Sintoma('Vómitos', 'AMARILLO', ['vomit', 'devolviendo']),
        Sintoma('Dolor abdominal', 'AMARILLO', ['dolor de estomago', 'dolor abdominal', 'dolor de barriga', 'dolor en el abdomen', 'me duele el estomago']),
        Sintoma('Dolor de cabeza fuerte', 'AMARILLO', ['dolor de cabeza fuerte', 'dolor de cabeza muy fuerte', 'migrana']),
        Sintoma('Mareo', 'AMARILLO', ['mareo', 'mareado', 'mareada']),
        Sintoma('Fractura o golpe fuerte', 'AMARILLO', ['fractura', 'hueso roto', 'golpe fuerte', 'me cai', 'accidente']),
        Sintoma('Herida', 'AMARILLO', ['herida', 'cortada', 'corte profundo']),
        Sintoma('Diarrea', 'AMARILLO', ['diarrea']),

        # Verde: puede esperar
        Sintoma('Tos', 'VERDE', ['tos']),
        Sintoma('Gripe o congestión', 'VERDE', ['gripe', 'resfriado', 'congestion', 'mocos', 'estornud']),
        Sintoma('Dolor de garganta', 'VERDE', ['dolor de garganta', 'me duele la garganta']),
        Sintoma('Dolor de cabeza leve', 'VERDE', ['dolor de cabeza', 'me duele la cabeza']),
        Sintoma('Dolor muscular', 'VERDE', ['dolor muscular', 'dolor de espalda', 'dolor de cuerpo']),
        Sintoma('Alergia leve', 'VERDE', ['picazon', 'ronchas', 'alergia']),
    ]

    def analizar(self, texto):
        """Devuelve la lista de síntomas (objetos Sintoma) encontrados en el texto."""
        texto = normalizar(texto or '')
        encontrados = [s for s in self.SINTOMAS if s.aparece_en(texto)]

        # Si ya se detectó el dolor de cabeza fuerte, no se repite el leve
        nombres = [s.nombre for s in encontrados]
        if 'Dolor de cabeza fuerte' in nombres:
            encontrados = [s for s in encontrados if s.nombre != 'Dolor de cabeza leve']
        return encontrados
