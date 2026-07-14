# Ejemplo 1: Dockerfile simple y correcto para una app Python
FROM python:3.12-slim

LABEL maintainer="equipo-devops@empresa.com"

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV PORT=8080
EXPOSE 8080/tcp

USER 1000

CMD ["python", "app.py"]
