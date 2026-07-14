#!/usr/bin/env python3
"""
lexer_dockerfile.py
--------------------------------------------------------------------
Analizador léxico (lexer) para archivos Dockerfile, construido desde
"cero" mediante expresiones regulares (módulo re de Python), siguiendo
el mismo esquema teórico visto en el Tema 4 (AFD representado mediante
regex, un patrón por componente léxico / token).

Universidad Nacional Experimental de Guayana
Lenguaje y Compiladores - Sección 01
Actividad 2 del Tema 4: Lexer para verificación de archivos Docker

Uso:
    python3 lexer_dockerfile.py <archivo_dockerfile>
    ./lexer_dockerfile.py <archivo_dockerfile>      (si tiene permiso de ejecución)

Si no se indica archivo, se lee desde la entrada estándar (stdin).
--------------------------------------------------------------------
"""

import re
import sys

# ---------------------------------------------------------------------------
# 1) Alfabeto de instrucciones válidas de un Dockerfile (palabras reservadas)
# ---------------------------------------------------------------------------
INSTRUCCIONES = [
    "FROM", "RUN", "CMD", "LABEL", "MAINTAINER", "EXPOSE", "ENV", "ADD",
    "COPY", "ENTRYPOINT", "VOLUME", "USER", "WORKDIR", "ARG", "ONBUILD",
    "STOPSIGNAL", "HEALTHCHECK", "SHELL",
]
_INSTR_ALT = "|".join(INSTRUCCIONES)

# ---------------------------------------------------------------------------
# 2) Tabla de tokens: (nombre_token, patron_regex)
#    El ORDEN importa: re.finditer intenta las alternativas en el orden en
#    que aparecen; por ello los patrones más específicos se ubican antes
#    que los patrones más generales (equivalente a resolver el conflicto
#    de "regla de mayor prioridad" que se da al construir el AFD a mano).
# ---------------------------------------------------------------------------
TOKENS = [
    # Comentarios: se ignoran, igual que en el ejemplo de /etc/network/interfaces
    ("COMMENT",        r"\#.*"),

    # Continuación de línea (backslash + salto de línea)
    ("LINECONT",       r"\\[ \t]*\r?\n"),

    # Directiva de parser (# syntax=... , # escape=...)
    ("PARSER_DIRECTIVE", r"(?i:\#\s*(?:syntax|escape)\s*=\s*\S+)"),

    # Instrucción Docker: solo se reconoce al inicio de línea (con posibles
    # espacios/tabs antes), sin distinguir mayúsculas/minúsculas, tal como
    # ocurre realmente en la especificación de Dockerfile.
    ("INSTRUCTION",    rf"(?im:^[ \t]*\b(?:{_INSTR_ALT})\b)"),

    # Palabra en mayúsculas al inicio de línea que NO es una instrucción
    # válida (p. ej. "FORM" en vez de "FROM"): se reporta como error léxico,
    # igual que el ejemplo de la lectura ("wile" en vez de "while").
    ("UNKNOWN_INSTRUCTION", r"(?m:^[ \t]*[A-Z][A-Z_]{1,}\b)"),

    # Bandera / flag de instrucción: --from=builder, -o, -y, --chown=user:group
    ("FLAG",           r"--?[a-zA-Z][a-zA-Z0-9-]*(?:=[^\s]+)?"),

    # Imagen con digest: nombre@sha256:<64 hex>
    ("IMAGE_DIGEST",   r"[a-zA-Z0-9][a-zA-Z0-9._/-]*@sha256:[a-fA-F0-9]{64}"),

    # Mapeo de puertos: 8080:80, 8080:80/tcp, 53:53/udp
    ("PORT_MAP",       r"\b\d{1,5}:\d{1,5}(?:/(?:tcp|udp))?\b"),

    # Puerto simple (EXPOSE 8080, EXPOSE 53/udp)
    ("PORT",           r"\b\d{1,5}/(?:tcp|udp)\b"),

    # Imagen base con tag: ubuntu:22.04, python:3.12-slim, myrepo/app:v1
    ("IMAGE_TAG",      r"\b[a-zA-Z0-9][a-zA-Z0-9._/-]*:[a-zA-Z0-9._-]+\b"),

    # Asignación de variable (ENV KEY=VALUE / ARG KEY=VALUE)
    ("ASSIGN",         r"\b[A-Za-z_][A-Za-z0-9_]*="),

    # Expansión de variable de entorno: $VAR, ${VAR}
    ("VARIABLE",       r"\$\{[A-Za-z_][A-Za-z0-9_]*\}|\$[A-Za-z_][A-Za-z0-9_]*"),

    # Cadenas entre comillas dobles o simples (forma exec / valores citados)
    ("STRING_DOUBLE",  r'"(?:[^"\\]|\\.)*"'),
    ("STRING_SINGLE",  r"'(?:[^'\\]|\\.)*'"),

    # Operadores de encadenamiento de shell usados dentro de RUN
    ("AND_OP",         r"&&"),
    ("PIPE_OP",        r"\|"),
    ("SEMI",           r";"),

    # Símbolos de la forma "exec" (arreglo JSON): [ "cmd", "arg1" ]
    ("LBRACKET",       r"\["),
    ("RBRACKET",       r"\]"),
    ("COMMA",          r","),

    # Rutas relativas mínimas: ".", "..", "./algo", "../algo"
    ("DOT_PATH",       r"\.{1,2}(?:/[^\s\"'\[\],]*)?"),

    # Rutas de archivo/directorio absolutas
    ("PATH",           r"/[^\s\"'\[\],]*"),

    # Números: enteros o con puntos tipo versión (22.04, 1.0.0)
    ("NUMBER",         r"\b\d+(?:\.\d+)*\b"),

    # Identificador genérico (nombres de imágenes, argumentos, valores, etc.)
    ("IDENTIFIER",     r"[A-Za-z_][A-Za-z0-9_.\-/]*"),

    # Fin de línea
    ("NEWLINE",        r"\n"),

    # Espacios y tabuladores: se ignoran
    ("SKIP",           r"[ \t]+"),

    # Cualquier otro carácter no reconocido -> error léxico
    ("MISMATCH",       r"."),
]

# Se compila una única expresión regular con grupos con nombre (?P<NOMBRE>patron)
# unidos por alternancia "|". Esta es la representación práctica del AFD que
# reconoce el lenguaje léxico de un Dockerfile: cada grupo con nombre equivale
# a un estado de aceptación distinto del autómata.
TOKEN_REGEX = re.compile(
    "|".join(f"(?P<{nombre}>{patron})" for nombre, patron in TOKENS)
)


class TokenLexico:
    """Representa un token reconocido: (tipo, lexema, linea, columna)."""

    __slots__ = ("tipo", "lexema", "linea", "columna")

    def __init__(self, tipo, lexema, linea, columna):
        self.tipo = tipo
        self.lexema = lexema
        self.linea = linea
        self.columna = columna

    def __repr__(self):
        return f"<{self.tipo} '{self.lexema}' L{self.linea}:C{self.columna}>"


def analizar(codigo_fuente):
    """
    Recorre 'codigo_fuente' carácter a carácter (mediante el autómata
    representado por TOKEN_REGEX) y produce dos listas:
      - tokens: lista de TokenLexico reconocidos correctamente
      - errores: lista de tuplas (lexema, linea, columna) con errores léxicos

    Este bucle de lectura es la implementación práctica de la tabla de
    transiciones del AFD descrita en la teoría: por cada estado final
    (token reconocido) el autómata regresa automáticamente al estado
    inicial para continuar leyendo hasta el final de la entrada.
    """
    tokens = []
    errores = []
    linea_num = 1
    inicio_linea = 0

    for match in TOKEN_REGEX.finditer(codigo_fuente):
        tipo = match.lastgroup
        lexema = match.group(tipo)
        columna = match.start() - inicio_linea + 1

        if tipo == "NEWLINE":
            linea_num += 1
            inicio_linea = match.end()
            continue
        if tipo == "LINECONT":
            linea_num += 1
            inicio_linea = match.end()
            continue
        if tipo in ("SKIP", "COMMENT", "PARSER_DIRECTIVE"):
            continue
        if tipo == "MISMATCH":
            errores.append((lexema, linea_num, columna,
                             "carácter no reconocido por el alfabeto del lenguaje"))
            continue
        if tipo == "UNKNOWN_INSTRUCTION":
            lexema = lexema.strip()
            errores.append((lexema, linea_num, columna,
                             "instrucción Docker no reconocida (¿error de escritura?)"))
            continue
        if tipo == "INSTRUCTION":
            lexema = lexema.strip()

        tokens.append(TokenLexico(tipo, lexema, linea_num, columna))

    return tokens, errores


def imprimir_resultado(tokens, errores, nombre_archivo="<stdin>"):
    print(f"=== Análisis léxico de: {nombre_archivo} ===\n")
    for tok in tokens:
        print(f"TOKEN: {tok.tipo:<16} Lexema: {tok.lexema:<30} "
              f"(línea {tok.linea}, columna {tok.columna})")

    print()
    if errores:
        print(f"--- Se encontraron {len(errores)} error(es) léxico(s) ---")
        for lexema, linea, columna, motivo in errores:
            print(f"ERROR LÉXICO: '{lexema}' en línea {linea}, "
                  f"columna {columna} -> {motivo}")
        print("\nRESULTADO: El archivo Dockerfile CONTIENE ERRORES LÉXICOS.")
    else:
        print("RESULTADO: El archivo Dockerfile es LÉXICAMENTE VÁLIDO "
              "(no se encontraron caracteres o lexemas no reconocidos).")

    print(f"\nTotal de tokens reconocidos: {len(tokens)}")
    print(f"Total de errores léxicos:   {len(errores)}")


def main():
    if len(sys.argv) > 1:
        ruta = sys.argv[1]
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
        except OSError as e:
            print(f"Error al abrir el archivo '{ruta}': {e}")
            sys.exit(1)
        nombre = ruta
    else:
        contenido = sys.stdin.read()
        nombre = "<stdin>"

    tokens, errores = analizar(contenido)
    imprimir_resultado(tokens, errores, nombre)

    # Código de salida: 0 si no hay errores léxicos, 1 si existen.
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
