# TriageVoz — Sistema de Reconocimiento de Voz para Triage

Proyecto 3 de la cátedra **Programación Orientada a Objetos** (Ciclo II, 2026) — PRY-TRI-003.

El sistema graba o recibe audio, lo numera, lo guarda y lo convierte a texto con **Whisper**. Está hecho con **Python + Django + SQLite**.

> El sistema es una herramienta de apoyo. La clasificación automática **no sustituye** el criterio del personal médico. Solo se usan datos ficticios.

---

## 1. Qué hace el sistema

Es una **grabadora de voz**: cada grabación se numera (Grabación 1, 2, 3...), el audio se guarda en una carpeta y el texto que saca **Whisper** se guarda en otra.

| Página | Ruta | Qué hace |
|---|---|---|
| Iniciar sesión | `/login/` | Solo entra quien tiene usuario y contraseña |
| Grabar | `/` | Graba con el micrófono (o sube un archivo). Lo numera, lo guarda y lo pasa a texto |
| Mis grabaciones | `/grabaciones/` | Lista numerada con buscador; se puede escuchar cada audio |
| Detalle | `/grabaciones/<id>/` | Escuchar, corregir el texto, descargar el `.txt`, volver a transcribir o eliminar |
| Administración | `/admin/` | Panel de Django |

### Dónde se guardan los archivos

```
media/
├── reconocimiento_de_voz/   grabacion_001.webm, grabacion_002.webm ...
└── transcripciones/         grabacion_001.txt,  grabacion_002.txt ...
```

### Clases de POO (carpeta `triage/services/`)

- **Transcriptor** (clase abstracta) → **TranscriptorWhisper** (herencia): pasa el audio a texto con Whisper.
- **ServicioTranscripcion**: usa cualquier Transcriptor (polimorfismo) y convierte los errores en mensajes claros (**TranscripcionError**).

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
│   ├── models.py               Grabacion (número, audio, texto)
│   ├── views.py                Lógica de cada página
│   ├── urls.py                 Rutas de la app
│   ├── admin.py                Panel /admin/
│   ├── tests.py                7 pruebas automáticas
│   ├── services/               Clases de POO para Whisper
│   └── ...
│
├── templates/                Páginas HTML (base.html es el diseño común)
├── static/                   style.css y script.js
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
