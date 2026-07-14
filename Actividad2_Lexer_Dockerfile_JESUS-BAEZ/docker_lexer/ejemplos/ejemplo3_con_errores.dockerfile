# Ejemplo 3: Dockerfile con errores léxicos intencionales
FORM ubuntu:22.04

RUN echo "hola mundo" && apt-get update && apt-get install -y curl

ENV RUTA=$RUTA:/usr/local/bin

LABEL vers~ion="1.0"

EXPOSE 80!81

CMD ["python", "app.py"]
