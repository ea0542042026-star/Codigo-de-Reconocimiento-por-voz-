# TriageVoz — Sistema de Reconocimiento de Voz para Triage

Proyecto 3 de la cátedra **Programación Orientada a Objetos** (Ciclo II, 2026) — PRY-TRI-003.

El sistema graba o recibe audio, lo convierte a texto con **Whisper**, extrae síntomas con **NLP** y propone una prioridad de atención. Está hecho con **Python + Django + SQLite**.

> El sistema es una herramienta de apoyo. La clasificación automática **no sustituye** el criterio del personal médico. Solo se usan datos ficticios.

---

## 1. Qué hace el sistema

| Página | Ruta | Qué hace |
|---|---|---|
| Iniciar sesión | `/login/` | Solo entra el personal con usuario y contraseña |
| Inicio | `/` | Panel con números reales, prioridades de hoy, cola de atención y actividad reciente |
| Pacientes | `/pacientes/` | Lista con buscador, nuevo, ver, editar y eliminar |
| Grabación | `/audio/` | Graba con el micrófono (o sube un archivo), lo guarda y lo transcribe con **Whisper** |
| Triage | `/registro/nuevo/` | Formulario: paciente, motivo, texto dictado y signos vitales. El botón **Analizar** sugiere la prioridad |
| Detalle | `/registro/<id>/` | Toda la evaluación, el audio, los síntomas detectados y el cambio de estado (En espera, En atención, Atendido) |
| Historial | `/historial/` | Todas las evaluaciones con buscador, filtros y descarga en CSV (Excel) |
| Reportes | `/reportes/` | Gráficas de los últimos 7 días, prioridades, estados y síntomas más comunes |
| Administración | `/admin/` | Panel de Django para manejar usuarios y datos |

### Cómo se decide la prioridad (POO)

- `services/analizador_sintomas.py` → **AnalizadorSintomas**: busca palabras clave en el texto (NLP sencillo) y devuelve los síntomas con su nivel.
- `services/clasificador_triage.py` → **Regla** (clase abstracta) y sus hijas **ReglaSintomas**, **ReglaSignosVitales** y **ReglaDolor**. **ClasificadorTriage** junta las reglas y elige el color más grave (polimorfismo).
- `services/transcriptor.py`, `transcriptor_whisper.py` y `servicio_transcripcion.py` → pasan el audio a texto con Whisper.

---

## 2. Cómo instalar el proyecto en tu computadora (Windows)

Necesitas **Python 3.10 o superior** y **Git**.

```powershell
# 1. Descargar el proyecto
git clone https://github.com/ea0542042026-star/Codigo-de-Reconocimiento-por-voz-.git
cd Codigo-de-Reconocimiento-por-voz-

# 2. Crear y encender el entorno virtual
py -m venv venv
.\venv\Scripts\activate
# Si sale un error de "ejecución de scripts", corre una sola vez:
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

# 3. Instalar las librerías (Whisper es pesado: tarda varios minutos)
python -m pip install -r requirements.txt
# Whisper necesita FFmpeg para leer el audio:
#   winget install ffmpeg   (luego cerrar y abrir VS Code)

# 4. Crear la base de datos, el usuario y datos de ejemplo
python manage.py migrate
python manage.py createsuperuser
python manage.py datos_demo        # opcional: 10 pacientes ficticios

# 5. Encender el servidor
python manage.py runserver
```

Abre **http://127.0.0.1:8000/** e inicia sesión con el usuario que creaste.

Para correr las pruebas automáticas: `python manage.py test triage`

> La carpeta `venv/`, la base de datos `db.sqlite3` y la carpeta `media/` **no se suben** a GitHub (están en `.gitignore`).

---

## 3. Estructura del proyecto

```
├── config/                     Configuración general (settings.py, urls.py)
├── triage/                     App principal
│   ├── models.py               Paciente y RegistroTriage
│   ├── forms.py                Formularios con validaciones
│   ├── views.py                Lógica de cada página
│   ├── urls.py                 Rutas de la app
│   ├── admin.py                Panel /admin/
│   ├── tests.py                16 pruebas automáticas
│   ├── services/               Clases de POO: Whisper, NLP y clasificador
│   ├── management/commands/    datos_demo (datos de ejemplo)
│   ├── templates/triage/       Páginas HTML (base.html es el diseño común)
│   └── static/triage/          style.css y script.js
├── manage.py
└── requirements.txt
```

---

## 4. Ramas del equipo

**Nadie sube directo a `main`.** Cada quien trabaja en su rama y los cambios entran por *pull request* hacia `develop`.

| Rama | Responsable | Módulo |
|---|---|---|
| `main` | Aldair (integración) | Versión estable |
| `develop` | Aldair (integración) | Integración de todos los módulos |
| `feature/integracion` | Aldair | Django, rutas y unión de módulos |
| `feature/audio` | Integrante 2 | Grabación y procesamiento de audio |
| `feature/transcripcion` | Integrante 3 | Whisper y transcripción |
| `feature/nlp` | Integrante asignado | Procesamiento de texto y clasificación |

Para trabajar en tu rama:

```powershell
git checkout feature/audio      # cambia a tu rama (usa la tuya)
git pull                        # trae lo último
# ... haces tus cambios ...
git add .
git commit -m "Descripción corta de lo que hiciste"
git push
```

Luego, en GitHub, abre un **Pull request** de tu rama hacia `develop`.

---

## 5. Equipo

| Integrante | Rol |
|---|---|
| Escobar Acosta Orlando Aldair | Integración (Django, rutas y unión de módulos) |
| Vásquez Maravilla Josué Daniel | Audio |
| Arguera Pérez Carlos Antonio | Whisper, IA y NLP |
| Xander Orlando Vásquez Ramírez | Pacientes, modelos e historial |
| Salgado Alvarenga Nelson Salvador | |

**Tecnologías:** Python 3.10+, Django 6.1.2, SQLite, OpenAI Whisper, Git y GitHub.
