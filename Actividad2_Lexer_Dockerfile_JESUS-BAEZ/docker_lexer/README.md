# Lexer para verificación de archivos Docker (Dockerfile)

## Contenido del paquete

```
docker_lexer/
├── README.md                          <- este archivo
├── src/
│   └── lexer_dockerfile.py            <- código fuente del lexer (Python + re)
├── ejecutable/
│   └── analizador_dockerfile          <- ejecutable de línea de comandos
├── ejemplos/
│   ├── ejemplo1_valido_simple.dockerfile
│   ├── ejemplo2_valido_multistage.dockerfile
│   └── ejemplo3_con_errores.dockerfile
└── resultados/
    ├── salida_ejemplo1.txt            <- salida real de la ejecución
    ├── salida_ejemplo2.txt
    └── salida_ejemplo3.txt
```

## Requisitos

- Python 3.8 o superior (no requiere librerías externas; usa únicamente el
  módulo estándar `re`).

## Ejecución

Desde la raíz del proyecto:

```bash
python3 src/lexer_dockerfile.py ejemplos/ejemplo1_valido_simple.dockerfile
```

o utilizando el ejecutable incluido (script con permisos de ejecución):

```bash
chmod +x ejecutable/analizador_dockerfile
./ejecutable/analizador_dockerfile ejemplos/ejemplo1_valido_simple.dockerfile
```

El lexer también puede recibir el archivo por entrada estándar:

```bash
cat ejemplos/ejemplo1_valido_simple.dockerfile | python3 src/lexer_dockerfile.py
```

El programa retorna código de salida `0` si el archivo es léxicamente
válido, y `1` si se detectaron errores léxicos.

## Descripción breve

El lexer reconoce las instrucciones reservadas de un Dockerfile (`FROM`,
`RUN`, `CMD`, `LABEL`, `ENV`, `COPY`, `ADD`, `EXPOSE`, `WORKDIR`, `USER`,
`ARG`, `VOLUME`, `ENTRYPOINT`, `ONBUILD`, `STOPSIGNAL`, `HEALTHCHECK`,
`SHELL`, `MAINTAINER`), así como imágenes con tag (`ubuntu:22.04`),
imágenes con digest (`alpine@sha256:...`), banderas (`--from=builder`,
`-y`), mapeos/puertos, asignaciones `CLAVE=valor`, cadenas, arreglos en
forma *exec*, rutas de archivo, comentarios y variables de entorno
(`$VAR`). Cualquier carácter o palabra que no encaje en ninguno de estos
patrones se reporta como **error léxico**, indicando línea y columna.

Ver el informe (documento Word) para el detalle paso a paso de la
construcción del lexer y el análisis de los 3 ejemplos de ejecución.
