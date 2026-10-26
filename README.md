# TriageVoz — Sistema de Reconocimiento de Voz para Triage

Proyecto 3 de la cátedra **Programación Orientada a Objetos** (Ciclo II, 2026) — PRY-TRI-003.

El sistema graba o recibe audio, lo convierte a texto con **Whisper**, extrae síntomas con **NLP** y propone una prioridad de atención. Está hecho con **Python + Django + SQLite**.

> El sistema es una herramienta de apoyo. La clasificación automática **no sustituye** el criterio del personal médico. Solo se usan datos ficticios.

---

## 1. Estado actual (26 de octubre de 2026)

| Semana | Tareas | Estado |
|---|---|---|
| 1 | T001–T006: repositorio, ramas y Django | ✅ Django funcionando |
| 2 | T007–T011: estructura y rutas | ✅ Rutas `/`, `/audio/`, `/audio/subir/` |
| 3 | T012–T016: módulo de audio | 🟡 Vista que recibe audio lista; falta la página de grabación (`audio.html`) y el módulo del integrante 2 |
| 4 | T017–T021: Whisper | ⏳ Pendiente |

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

# 3. Instalar las librerías
python -m pip install -r requirements.txt

# 4. Crear la base de datos y la carpeta de audios
python manage.py migrate
mkdir media\audios

# 5. Encender el servidor
python manage.py runserver
```

Abre **http://127.0.0.1:8000/** en el navegador. Debe aparecer el panel del administrador.

> La carpeta `venv/`, la base de datos `db.sqlite3` y la carpeta `media/` **no se suben** a GitHub (están en `.gitignore`). Cada integrante las crea en su computadora con los pasos de arriba.

---

## 3. Estructura del proyecto

```
├── config/                  Configuración general del proyecto
│   ├── settings.py          Apps, base de datos, static y media (MEDIA_URL, MEDIA_ROOT)
│   └── urls.py              Rutas generales: admin/ e include('triage.urls')
├── triage/                  App principal del sistema
│   ├── views.py             inicio, pagina_audio, subir_audio
│   ├── urls.py              Rutas de la app
│   ├── templates/triage/
│   │   └── index.html       Panel del administrador
│   └── static/triage/
│       ├── style.css        Diseño del panel
│       └── script.js        Botones del panel (menú, campana, usuario, acciones)
├── manage.py                Comandos de Django (runserver, migrate, etc.)
├── requirements.txt         Librerías necesarias
└── .gitignore               Archivos que Git no sube
```

---

## 4. Rutas disponibles

| Ruta | Vista | Qué hace |
|---|---|---|
| `/` | `inicio` | Muestra el panel del administrador |
| `/audio/` | `pagina_audio` | Página para grabar audio *(la plantilla `audio.html` está pendiente, T016)* |
| `/audio/subir/` | `subir_audio` | Recibe el audio por **POST**, revisa formato (wav, mp3, webm, m4a, ogg) y tamaño (máx. 25 MB) y lo guarda en `media/audios/` |
| `/admin/` | Admin de Django | Panel de administración (requiere `python manage.py createsuperuser`) |

> Si abres `/audio/subir/` escribiendo la dirección en el navegador sale **HTTP 405**. Es normal: esa ruta solo acepta envíos de audio (POST).

---

## 5. Ramas del equipo

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

## 6. Equipo

| Integrante | Rol |
|---|---|
| Escobar Acosta Orlando Aldair | Integración (Django, rutas y unión de módulos) |
| Vásquez Maravilla Josué Daniel | |
| Arguera Pérez Carlos Antonio | |
| Xander Orlando Vásquez Ramírez | |
| Salgado Alvarenga Nelson Salvador | |

**Tecnologías:** Python 3.10+, Django 6.1.2, SQLite, OpenAI Whisper, Git y GitHub.
