# Docker desde cero: lista de tareas con Flask y PostgreSQL

El proyecto del video «Docker desde cero». Es una lista de tareas en Python (Flask + gunicorn)
que guarda los datos en PostgreSQL 18. Cada pieza corre en su contenedor.

```
docker-tareas/
├── app.py              la app web: lista, agrega y marca tareas
├── templates/
│   └── index.html      la página
├── requirements.txt    Flask, gunicorn y psycopg, con versión fija
├── Dockerfile          la receta de la imagen de la app
├── .dockerignore       lo que no entra a la imagen (entre otras cosas, .env)
├── compose.yaml        la app y la base, juntas
└── .env.example        la contraseña de ejemplo; se copia a .env
```

## Lo que necesitan

Solo Docker. No hace falta instalar Python ni PostgreSQL.

- **Windows o Mac:** Docker Desktop (https://docs.docker.com/desktop/). En Windows usa WSL 2.
- **Linux:** Docker Engine con el plugin de Compose (https://docs.docker.com/engine/install/).

Comprueben la instalación con `docker version` y `docker run hello-world`.

## Levantar todo con un comando

```bash
cp .env.example .env          # en Windows (PowerShell): copy .env.example .env
docker compose up -d --build
```

Abran http://localhost:8000. Para ver qué está corriendo y los registros:

```bash
docker compose ps
docker compose logs -f web
```

Para detener:

```bash
docker compose down           # borra los contenedores y la red; las tareas quedan en el volumen
docker compose down -v        # borra también el volumen: se pierden las tareas
```

Cambien la contraseña de `.env` antes de usarlo en serio. Ojo: Postgres solo la toma la primera
vez, con el volumen vacío. Si ya levantaron el proyecto, hagan `docker compose down -v` para que
la nueva contraseña se aplique (y se pierdan las tareas).

## Paso a paso, sin Compose (como en el video)

```bash
# 1. Una base PostgreSQL 18 con un volumen para los datos
docker network create red-tareas
docker run -d --name db --network red-tareas \
  -e POSTGRES_PASSWORD=secreto \
  -v pgdata:/var/lib/postgresql \
  postgres:18

# 2. La imagen de la app
docker build -t tareas:1.0 .

# 3. La app, en la misma red, apuntando a la base por su nombre: db
docker run -d --name web --network red-tareas -p 8000:8000 \
  -e DATABASE_URL=postgresql://postgres:secreto@db:5432/postgres \
  tareas:1.0
```

Para limpiar lo que crearon a mano:

```bash
docker rm -f web db
docker network rm red-tareas
docker volume rm pgdata
```

## Si algo falla

| Síntoma | Causa | Solución |
|---|---|---|
| La app muere con `connection to server at "127.0.0.1", port 5432 failed` | Dentro de un contenedor, `localhost` es el propio contenedor | Apunten a la base por su nombre (`@db:5432`) y pongan los dos contenedores en la misma red |
| Postgres se detiene al arrancar con `Error: in 18+, these Docker images are configured…` | Postgres 18 cambió la carpeta de los datos | Monten el volumen en `/var/lib/postgresql`, no en `/var/lib/postgresql/data` |
| Las tareas desaparecen al borrar el contenedor | No había un volumen con nombre | `-v pgdata:/var/lib/postgresql` (o el volumen `datos` de `compose.yaml`) |
| `port is already allocated` | Otro contenedor o programa ya usa el puerto 8000 | `docker ps -a` para encontrarlo, o cambien el primer número: `-p 8001:8000` |
| La página no carga aunque el contenedor está arriba | El servidor escucha solo en 127.0.0.1 dentro del contenedor | En el `CMD`, `--bind 0.0.0.0:8000` (ya está en el `Dockerfile`) |
| Cambié `app.py` y no veo el cambio | El código está dentro de la imagen | `docker compose up -d --build` |

Probado el 15 de octubre de 2026 con Docker Desktop 4.82 (Engine 29.6.1, Compose v5.3.0) en un Mac
con Apple silicon, `python:3.14-slim-trixie` y `postgres:18` (18.6).
