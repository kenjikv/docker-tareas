# 1. La base: Python 3.14 sobre Debian 13 (trixie), en su versión liviana
FROM python:3.14-slim-trixie

# 2. Todo lo que sigue pasa dentro de /app
WORKDIR /app

# 3. Primero solo las dependencias: esta capa se reutiliza mientras requirements.txt no cambie
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Después el código
COPY . .

# 5. Un usuario sin privilegios: la app no corre como root
RUN useradd --create-home appuser
USER appuser

# 6. El puerto en el que escucha la app (solo es documentación)
EXPOSE 8000

# 7. El comando al arrancar: gunicorn sirve la app en el puerto 8000, abierta a todas las interfaces
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "app:app"]
