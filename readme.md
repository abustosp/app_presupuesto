# 🚢 Backend Autogestionado para Presupuesto Interactivo

El proyecto dejó de depender de Firebase y ahora incluye un backend open source basado en **FastAPI + SQLite**. Todo se ejecuta en contenedores Docker para que puedas levantar la aplicación con un solo comando.

## 📦 ¿Qué se incluye?

- **FastAPI** para exponer los endpoints REST (`/api`).
- **SQLite** como base de datos embebida (persistida en un volumen Docker).
- **Uvicorn** como servidor ASGI.
- `Dockerfile` y `docker-compose.yaml` listos para levantar la app completa.

## ⚙️ Variables de entorno

Configura las variables en el archivo `.env` (puedes partir de `.env.example`):

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `APP_PORT` | Puerto expuesto en tu máquina | `8000` |
| `DATABASE_URL` | Cadena de conexión SQLAlchemy | `sqlite:///./data/app.db` |
| `ALLOWED_ORIGINS` | Orígenes permitidos para CORS (usa `*` para todos) | `*` |

## ▶️ Levantar el stack

```bash
cp .env.example .env  # solo la primera vez
# Ajusta las variables que necesites

docker compose up -d
```

La aplicación quedará disponible en [http://localhost:8000](http://localhost:8000).

## 🔌 Endpoints principales

- `GET /` → Sirve `presupuesto.html` con la interfaz del simulador.
- `GET /api/health` → Chequeo de salud del backend.
- `GET /api/budgets` → Lista presupuestos guardados.
- `POST /api/budgets` → Guarda un nuevo presupuesto.
- `GET /api/budgets/{id}` → Obtiene un presupuesto existente.
- `PUT /api/budgets/{id}` → Actualiza un presupuesto.
- `DELETE /api/budgets/{id}` → Elimina un presupuesto.

## 💾 Persistencia

- Los datos se almacenan en `data/app.db` dentro del contenedor.
- El volumen `budget_data` declarado en `docker-compose.yaml` garantiza que la información persista entre reinicios.

## 🔐 Seguridad

- Puedes restringir los orígenes habilitados configurando `ALLOWED_ORIGINS` (por ejemplo `https://midominio.com`).
- Para despliegues productivos considera proteger el servicio detrás de un proxy con HTTPS y autenticación.

## 🧪 Desarrollo local sin Docker

Si prefieres ejecutar sin contenedores:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Luego abre `http://localhost:8000`.

¡Listo! Ahora la app es totalmente autogestionada y sin dependencias propietarias.
