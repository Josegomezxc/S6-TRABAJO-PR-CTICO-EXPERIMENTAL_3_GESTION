# 🛡️ DockerShield

**Prototipo universitario — UNEMI**  
Plataforma de seguridad de correo electrónico con análisis de adjuntos basado en contenedores Docker.

---

## 🐳 Docker

DockerShield está diseñado para ejecutarse enteramente en contenedores. El flujo de trabajo de desarrollo y despliegue gira en torno a Docker.

### Requisitos

- Docker Engine 24+
- Docker Compose v2+

### Inicio rápido

```bash
docker compose up --build
```

Esto construye la imagen e inicia el contenedor `dockershield-web` en `http://localhost:8000` con las migraciones aplicadas automáticamente.

### Modo desarrollo

El `docker-compose.yml` monta el directorio actual como volumen en `/app`, lo que permite editar código en caliente — Django recarga automáticamente los cambios.

```bash
# Solo reconstruir si cambias requirements.txt o el Dockerfile
docker compose up --build

# En ejecución, los cambios en .py/.html se reflejan al instante
```

---

## 📦 Componentes Docker

### Dockerfile

- **Base**: `python:3.12-slim` — imagen oficial mínima de Python
- **Dependencias del sistema**: `gcc`, `libjpeg-dev`, `zlib1g-dev`, `libfreetype-dev` (necesarios para Pillow)
- **Python**: `pip install --no-cache-dir` con cache deshabilitado
- **Seguridad**: usuario no-root `dockershield` (UID 1000)
- **Puerto**: 8000
- **Entrypoint**: servidor de desarrollo de Django

### docker-compose.yml

```yaml
services:
  web:
    build: .
    container_name: dockershield-web
    ports:
      - "8000:8000"
    volumes:
      - .:/app              # monta el código fuente
    env_file:
      - .env                # variables de entorno
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.development
    command: >
      sh -c "python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"
```

### .dockerignore

```
ent_email/                 # entorno virtual local
.venv/ venv/               # entornos virtuales alternativos
__pycache__/ *.pyc         # archivos compilados
.env                       # variables de entorno (secretos)
.git/ .gitignore           # metadatos de git
README.md                  # documentación
db.sqlite3                 # base de datos local
.docker/                   # configuraciones docker locales
```

---

## 🌐 Variables de entorno

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `SECRET_KEY` | (obligatorio) | Clave secreta de Django |
| `DEBUG` | `True` | Modo depuración (desactivar en producción) |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Hosts permitidos |

Se cargan desde `.env` automáticamente vía `env_file` en docker-compose.

---

## 🏗️ Estructura del proyecto

```
PROTOTIPO-DOCKERSHIELD/
├── Dockerfile              # Imagen del contenedor
├── docker-compose.yml      # Orquestación del servicio
├── .dockerignore           # Exclusiones del build
├── .env                    # Variables de entorno
├── requirements.txt        # Dependencias Python
├── manage.py               # CLI de Django
├── config/                 # Configuración Django
│   └── settings/
│       ├── base.py         # Settings comunes
│       ├── development.py  # Settings desarrollo
│       ├── production.py   # Settings producción
│       └── testing.py      # Settings testing
├── apps/                   # Módulos de la aplicación
│   ├── core/               # Utilidades, panel admin, mock data
│   ├── accounts/           # Autenticación y perfiles
│   ├── aliases/            # Gestión de alias de correo
│   ├── mail/               # Bandeja de entrada, enviados, borradores
│   ├── sandbox/            # Análisis de adjuntos (sandbox)
│   └── notifications/      # Sistema de notificaciones
├── templates/              # Plantillas globales (error pages)
└── ent_email/              # Entorno virtual local (excluido por .dockerignore)
```

---

## 🧱 Arquitectura de apps

| App | Función |
|---|---|
| `core` | Panel admin, stats, validadores, contexto global |
| `accounts` | Login, registro, perfil, recuperación de cuenta |
| `aliases` | Alias desechables, solicitudes de cuota |
| `mail` | Dashboard, inbox, enviados, papelera, borradores |
| `sandbox` | Análisis de adjuntos (mock data en prototipo) |
| `notifications` | Alertas, reenvíos, notificaciones del sistema |

---

## ✅ Buenas prácticas Docker aplicadas

- **Imagen oficial slim** — `python:3.12-slim` reduce superficie de ataque
- **Pin de versiones** — Python 3.12, Django 5.2.13, Pillow 12.2.0
- **Usuario no-root** — `dockershield` (UID 1000) ejecuta la app
- **Cache deshabilitado** — `--no-cache-dir` y `rm -rf /var/lib/apt/lists/*`
- **.dockerignore estricto** — excluye secretos, venvs, cachés, git
- **Puerto único** — solo 8000 expuesto al host
- **PYTHONUNBUFFERED=1** — logs en tiempo real

---

## 🚀 Próximos pasos (producción)

- Perfil `config.settings.production` con Gunicorn / uWSGI
- Base de datos PostgreSQL en un contenedor separado
- Volumen persistente para base de datos y media
- Multi-stage build para reducir tamaño de imagen final
- Healthcheck en el Dockerfile
- Docker-in-Docker para el sandbox de adjuntos (aislamiento real)
- Orquestación con `docker stack` o Kubernetes

---

## 📄 Licencia

Proyecto académico — Universidad Estatal de Milagro (UNEMI), Ecuador.
