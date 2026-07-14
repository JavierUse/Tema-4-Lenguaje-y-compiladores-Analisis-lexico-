**Actividad 2: Construcción de un Lexer para la Verificación de Archivos Docker mediante Expresiones Regulares**

Nombre: Jesus Baez C.I:26753871

**Introducción**

El presente informe documenta el desarrollo de la Actividad 2 del Tema 4 (Análisis Léxico) de la asignatura Lenguaje y Compiladores. El objetivo es construir, desde cero y mediante expresiones regulares, un analizador léxico (lexer) capaz de tokenizar y verificar archivos Docker (Dockerfile), siguiendo el mismo esquema conceptual estudiado en clase: un autómata finito determinístico (AFD) cuyo comportamiento se representa de forma práctica mediante un conjunto de patrones regex asociados a cada componente léxico del lenguaje.

Un Dockerfile es el archivo de texto plano que describe, mediante una secuencia de instrucciones (FROM, RUN, COPY, CMD, ENV, EXPOSE, etc.), cómo construir una imagen de contenedor Docker. Al igual que el archivo /etc/network/interfaces revisado como ejemplo en el material del tema, un Dockerfile posee una estructura léxica bien definida: directivas reservadas, comentarios, valores (rutas, números, cadenas, pares clave=valor) y símbolos especiales. Esto lo convierte en un caso de estudio adecuado para aplicar la teoría de autómatas finitos y lenguajes regulares al diseño de un analizador léxico real.

**Fundamento Teórico Aplicado**

De acuerdo con la teoría revisada, todo compilador requiere un mecanismo inicial —el analizador léxico— que lea el programa fuente carácter a carácter y reconozca los componentes léxicos (tokens) definidos para el lenguaje L. Dado que los tokens de un lenguaje de programación son, en la práctica, expresiones regulares, y que los lenguajes regulares son reconocidos por un AFD (Q, Σ, δ, q0, F), es posible evitar la construcción manual de la tabla de transiciones del autómata y, en su lugar, codificar directamente cada estado de aceptación como un patrón regex con nombre. La unión de todos los patrones mediante alternancia ( | ) conforma una única expresión regular que actúa como el autómata completo: cada vez que se alcanza un estado de aceptación (un token reconocido) el proceso regresa automáticamente al estado inicial para continuar leyendo, tal como se describe en el material del Tema 4.

Esta actividad corresponde al enfoque "desde cero con regex" (a diferencia del enfoque con metacompilador como Flex, usado en el ejemplo del archivo interfaces de Debian). Se utilizó el lenguaje Python y su módulo estándar re, aplicando la misma técnica de grupos con nombre (?P<TOKEN>patrón) y re.finditer() presentada en el ejemplo de referencia del material del tema.

**Diseño del Lenguaje L (Dockerfile)**

Antes de construir el lexer se delimitó el subconjunto léxico del lenguaje Dockerfile que se desea reconocer:

* Instrucciones reservadas: FROM, RUN, CMD, LABEL, MAINTAINER, EXPOSE, ENV, ADD, COPY, ENTRYPOINT, VOLUME, USER, WORKDIR, ARG, ONBUILD, STOPSIGNAL, HEALTHCHECK, SHELL.
* Comentarios que inician con # (se ignoran, no generan token).
* Imágenes base, con o sin tag (imagen:tag) y con o sin digest (imagen@sha256:...).
* Banderas de instrucción de una o dos guiones (-y, --from=builder, --chown=usuario:grupo).
* Asignaciones clave=valor (usadas por ENV y ARG) y expansión de variables ($VAR).
* Cadenas entre comillas y arreglos en forma exec: [ "cmd", "arg1" ].
* Rutas absolutas y relativas, números (incluyendo notación de versión 1.0.0), mapeos y números de puerto.
* Operadores de encadenamiento de shell dentro de RUN: &&, |, ;.

La Tabla 1 resume el conjunto final de tokens definidos y su patrón regex asociado (se muestra la forma resumida; el patrón completo se encuentra en el código fuente lexer\_dockerfile.py).

Tabla 1. Componentes léxicos (tokens) del lexer

| **Token** | **Patrón regex (resumido)** | **Ejemplo de lexema** |
| --- | --- | --- |
| COMMENT | #.\* | # comentario |
| INSTRUCTION | ^(FROM|RUN|CMD|...)\b | FROM, RUN, COPY |
| UNKNOWN\_INSTRUCTION | ^[A-Z][A-Z\_]{1,}\b | FORM (typo de FROM) |
| FLAG | --?[a-zA-Z][a-zA-Z0-9-]\*(=...)? | --from=builder, -y |
| IMAGE\_DIGEST | nombre@sha256:[0-9a-f]{64} | alpine@sha256:c158... |
| PORT\_MAP | \d{1,5}:\d{1,5}(/tcp|/udp)? | 8080:80/tcp |
| PORT | \d{1,5}/(tcp|udp) | 8080/tcp |
| IMAGE\_TAG | nombre:tag | python:3.12-slim |
| ASSIGN | [A-Za-z\_][A-Za-z0-9\_]\*= | PORT=, BUILD\_VERSION= |
| VARIABLE | \$VAR | ${VAR} | $RUTA |
| STRING\_DOUBLE/SINGLE | "..." | '...' | "python" |
| AND\_OP / PIPE\_OP / SEMI | && | \| | ; | && |
| LBRACKET / RBRACKET / COMMA | [ | ] | , | [ "a", "b" ] |
| DOT\_PATH | \.{1,2}(/...)? | . .. ./cmd |
| PATH | /[^ \t"']\* | /usr/local/bin |
| NUMBER | \d+(\.\d+)\* | 8080, 1.0.0 |
| IDENTIFIER | [A-Za-z\_][A-Za-z0-9\_.\-/]\* | requirements.txt |
| NEWLINE / SKIP | \n | [ \t]+ | (se ignoran) |
| MISMATCH | . | carácter no reconocido |

**Construcción del Lexer Paso a Paso**

El desarrollo siguió los mismos pasos generales descritos en la teoría del Tema 4 para construir un analizador léxico basado en regex, adaptados al lenguaje Dockerfile:

## Paso 1 - Delimitar el alfabeto y las palabras reservadas

Se listó el conjunto de instrucciones válidas de un Dockerfile (variable INSTRUCCIONES) y se generó, mediante join, la alternancia regex correspondiente (\_INSTR\_ALT). Esta lista actúa como el vocabulario reservado del lenguaje L, equivalente al conjunto de estados de aceptación 'palabra clave' del AFD.

## Paso 2 - Definir un patrón regex por cada componente léxico

Se creó la lista TOKENS con tuplas (nombre\_token, patrón\_regex): cada patrón equivale a un estado de aceptación distinto del autómata (COMMENT, INSTRUCTION, FLAG, IMAGE\_TAG, IMAGE\_DIGEST, PORT, PORT\_MAP, ASSIGN, VARIABLE, STRING, LBRACKET/RBRACKET/COMMA, PATH, NUMBER, IDENTIFIER, NEWLINE, SKIP y, finalmente, MISMATCH como estado de error).

## Paso 3 - Resolver conflictos de prioridad entre patrones

Al igual que ocurre al construir un AFD a mano, varios patrones pueden coincidir con la misma entrada (por ejemplo, '8080:80/tcp' podría interpretarse como IMAGE\_TAG o como PORT\_MAP). Este conflicto se resolvió mediante el ORDEN de las alternativas dentro de la expresión regular combinada: Python re.finditer() prueba las alternativas en el orden en que aparecen, por lo que los patrones más específicos (IMAGE\_DIGEST, PORT\_MAP, PORT) se colocaron antes que los patrones más generales (IMAGE\_TAG, IDENTIFIER).

## Paso 4 - Combinar todos los patrones en una única expresión regular con grupos con nombre

Se construyó TOKEN\_REGEX uniendo todas las tuplas con el patrón (?P<NOMBRE>patrón) separadas por '|'. Esta expresión única es, en la práctica, la representación compacta del autómata finito completo que reconoce el lenguaje léxico de un Dockerfile.

## Paso 5 - Implementar el bucle de lectura (tabla de transiciones)

La función analizar(codigo\_fuente) recorre el texto de entrada con TOKEN\_REGEX.finditer(), lo que emula la lectura carácter a carácter descrita en la teoría: por cada coincidencia se determina el tipo de token (match.lastgroup), se descartan los tokens que deben ignorarse (SKIP, COMMENT, NEWLINE) y se contabiliza la posición (línea y columna) para fines de reporte.

## Paso 6 - Definir los estados fallidos y el reporte de errores

Siguiendo la recomendación teórica de no detener el análisis en el primer error, el patrón MISMATCH ('.', cualquier carácter) actúa como estado fallido: captura cualquier carácter no reconocido por ningún patrón anterior, lo registra en la lista de errores (lexema, línea, columna, motivo) y el autómata regresa automáticamente al estado inicial para continuar leyendo el resto del archivo. Se agregó además el token UNKNOWN\_INSTRUCTION para detectar palabras en mayúsculas al inicio de línea que no correspondan a ninguna instrucción Docker válida (por ejemplo, FORM en lugar de FROM), replicando el ejemplo de la lectura sobre identificadores no reconocidos (wile en vez de while).

## Paso 7 - Construir la interfaz de línea de comandos

La función main() permite ejecutar el lexer sobre un archivo pasado como argumento (python3 lexer\_dockerfile.py archivo) o leyendo desde la entrada estándar, e imprime cada token reconocido junto con su lexema, línea y columna, así como un resumen final indicando si el archivo es léxicamente válido o si contiene errores. El código de salida del proceso es 0 (válido) o 1 (con errores), útil para integrarlo en un pipeline de verificación (CI/CD).

## Paso 8 - Validar el lexer con casos de prueba

Finalmente se diseñaron tres Dockerfiles de prueba —dos válidos (uno simple y uno multi-stage) y uno con errores léxicos intencionales— para verificar que el lexer clasifica correctamente los tokens y detecta los errores esperados. Los resultados se documentan en la sección 6.

**Código Fuente del Lexer**

|  |
| --- |
| #!/usr/bin/env python3  """  lexer\_dockerfile.py  --------------------------------------------------------------------  Analizador léxico (lexer) para archivos Dockerfile, construido desde  "cero" mediante expresiones regulares (módulo re de Python), siguiendo  el mismo esquema teórico visto en el Tema 4 (AFD representado mediante  regex, un patrón por componente léxico / token).    Universidad Nacional Experimental de Guayana  Lenguaje y Compiladores - Sección 01  Actividad 2 del Tema 4: Lexer para verificación de archivos Docker    Uso:  python3 lexer\_dockerfile.py <archivo\_dockerfile>  ./lexer\_dockerfile.py <archivo\_dockerfile> (si tiene permiso de ejecución)    Si no se indica archivo, se lee desde la entrada estándar (stdin).  --------------------------------------------------------------------  """    import re  import sys    # ---------------------------------------------------------------------------  # 1) Alfabeto de instrucciones válidas de un Dockerfile (palabras reservadas)  # ---------------------------------------------------------------------------  INSTRUCCIONES = [  "FROM", "RUN", "CMD", "LABEL", "MAINTAINER", "EXPOSE", "ENV", "ADD",  "COPY", "ENTRYPOINT", "VOLUME", "USER", "WORKDIR", "ARG", "ONBUILD",  "STOPSIGNAL", "HEALTHCHECK", "SHELL",  ]  \_INSTR\_ALT = "|".join(INSTRUCCIONES)    # ---------------------------------------------------------------------------  # 2) Tabla de tokens: (nombre\_token, patron\_regex)  # El ORDEN importa: re.finditer intenta las alternativas en el orden en  # que aparecen; por ello los patrones más específicos se ubican antes  # que los patrones más generales (equivalente a resolver el conflicto  # de "regla de mayor prioridad" que se da al construir el AFD a mano).  # ---------------------------------------------------------------------------  TOKENS = [  # Comentarios: se ignoran, igual que en el ejemplo de /etc/network/interfaces  ("COMMENT", r"\#.\*"),    # Continuación de línea (backslash + salto de línea)  ("LINECONT", r"\\[ \t]\*\r?\n"),    # Directiva de parser (# syntax=... , # escape=...)  ("PARSER\_DIRECTIVE", r"(?i:\#\s\*(?:syntax|escape)\s\*=\s\*\S+)"),    # Instrucción Docker: solo se reconoce al inicio de línea (con posibles  # espacios/tabs antes), sin distinguir mayúsculas/minúsculas, tal como  # ocurre realmente en la especificación de Dockerfile.  ("INSTRUCTION", rf"(?im:^[ \t]\*\b(?:{\_INSTR\_ALT})\b)"),    # Palabra en mayúsculas al inicio de línea que NO es una instrucción  # válida (p. ej. "FORM" en vez de "FROM"): se reporta como error léxico,  # igual que el ejemplo de la lectura ("wile" en vez de "while").  ("UNKNOWN\_INSTRUCTION", r"(?m:^[ \t]\*[A-Z][A-Z\_]{1,}\b)"),    # Bandera / flag de instrucción: --from=builder, -o, -y, --chown=user:group  ("FLAG", r"--?[a-zA-Z][a-zA-Z0-9-]\*(?:=[^\s]+)?"),    # Imagen con digest: nombre@sha256:<64 hex>  ("IMAGE\_DIGEST", r"[a-zA-Z0-9][a-zA-Z0-9.\_/-]\*@sha256:[a-fA-F0-9]{64}"),    # Mapeo de puertos: 8080:80, 8080:80/tcp, 53:53/udp  ("PORT\_MAP", r"\b\d{1,5}:\d{1,5}(?:/(?:tcp|udp))?\b"),    # Puerto simple (EXPOSE 8080, EXPOSE 53/udp)  ("PORT", r"\b\d{1,5}/(?:tcp|udp)\b"),    # Imagen base con tag: ubuntu:22.04, python:3.12-slim, myrepo/app:v1  ("IMAGE\_TAG", r"\b[a-zA-Z0-9][a-zA-Z0-9.\_/-]\*:[a-zA-Z0-9.\_-]+\b"),    # Asignación de variable (ENV KEY=VALUE / ARG KEY=VALUE)  ("ASSIGN", r"\b[A-Za-z\_][A-Za-z0-9\_]\*="),    # Expansión de variable de entorno: $VAR, ${VAR}  ("VARIABLE", r"\$\{[A-Za-z\_][A-Za-z0-9\_]\*\}|\$[A-Za-z\_][A-Za-z0-9\_]\*"),    # Cadenas entre comillas dobles o simples (forma exec / valores citados)  ("STRING\_DOUBLE", r'"(?:[^"\\]|\\.)\*"'),  ("STRING\_SINGLE", r"'(?:[^'\\]|\\.)\*'"),    # Operadores de encadenamiento de shell usados dentro de RUN  ("AND\_OP", r"&&"),  ("PIPE\_OP", r"\|"),  ("SEMI", r";"),    # Símbolos de la forma "exec" (arreglo JSON): [ "cmd", "arg1" ]  ("LBRACKET", r"\["),  ("RBRACKET", r"\]"),  ("COMMA", r","),    # Rutas relativas mínimas: ".", "..", "./algo", "../algo"  ("DOT\_PATH", r"\.{1,2}(?:/[^\s\"'\[\],]\*)?"),    # Rutas de archivo/directorio absolutas  ("PATH", r"/[^\s\"'\[\],]\*"),    # Números: enteros o con puntos tipo versión (22.04, 1.0.0)  ("NUMBER", r"\b\d+(?:\.\d+)\*\b"),    # Identificador genérico (nombres de imágenes, argumentos, valores, etc.)  ("IDENTIFIER", r"[A-Za-z\_][A-Za-z0-9\_.\-/]\*"),    # Fin de línea  ("NEWLINE", r"\n"),    # Espacios y tabuladores: se ignoran  ("SKIP", r"[ \t]+"),    # Cualquier otro carácter no reconocido -> error léxico  ("MISMATCH", r"."),  ]    # Se compila una única expresión regular con grupos con nombre (?P<NOMBRE>patron)  # unidos por alternancia "|". Esta es la representación práctica del AFD que  # reconoce el lenguaje léxico de un Dockerfile: cada grupo con nombre equivale  # a un estado de aceptación distinto del autómata.  TOKEN\_REGEX = re.compile(  "|".join(f"(?P<{nombre}>{patron})" for nombre, patron in TOKENS)  )      class TokenLexico:  """Representa un token reconocido: (tipo, lexema, linea, columna)."""    \_\_slots\_\_ = ("tipo", "lexema", "linea", "columna")    def \_\_init\_\_(self, tipo, lexema, linea, columna):  self.tipo = tipo  self.lexema = lexema  self.linea = linea  self.columna = columna    def \_\_repr\_\_(self):  return f"<{self.tipo} '{self.lexema}' L{self.linea}:C{self.columna}>"      def analizar(codigo\_fuente):  """  Recorre 'codigo\_fuente' carácter a carácter (mediante el autómata  representado por TOKEN\_REGEX) y produce dos listas:  - tokens: lista de TokenLexico reconocidos correctamente  - errores: lista de tuplas (lexema, linea, columna) con errores léxicos    Este bucle de lectura es la implementación práctica de la tabla de  transiciones del AFD descrita en la teoría: por cada estado final  (token reconocido) el autómata regresa automáticamente al estado  inicial para continuar leyendo hasta el final de la entrada.  """  tokens = []  errores = []  linea\_num = 1  inicio\_linea = 0    for match in TOKEN\_REGEX.finditer(codigo\_fuente):  tipo = match.lastgroup  lexema = match.group(tipo)  columna = match.start() - inicio\_linea + 1    if tipo == "NEWLINE":  linea\_num += 1  inicio\_linea = match.end()  continue  if tipo == "LINECONT":  linea\_num += 1  inicio\_linea = match.end()  continue  if tipo in ("SKIP", "COMMENT", "PARSER\_DIRECTIVE"):  continue  if tipo == "MISMATCH":  errores.append((lexema, linea\_num, columna,  "carácter no reconocido por el alfabeto del lenguaje"))  continue  if tipo == "UNKNOWN\_INSTRUCTION":  lexema = lexema.strip()  errores.append((lexema, linea\_num, columna,  "instrucción Docker no reconocida (¿error de escritura?)"))  continue  if tipo == "INSTRUCTION":  lexema = lexema.strip()    tokens.append(TokenLexico(tipo, lexema, linea\_num, columna))    return tokens, errores      def imprimir\_resultado(tokens, errores, nombre\_archivo="<stdin>"):  print(f"=== Análisis léxico de: {nombre\_archivo} ===\n")  for tok in tokens:  print(f"TOKEN: {tok.tipo:<16} Lexema: {tok.lexema:<30} "  f"(línea {tok.linea}, columna {tok.columna})")    print()  if errores:  print(f"--- Se encontraron {len(errores)} error(es) léxico(s) ---")  for lexema, linea, columna, motivo in errores:  print(f"ERROR LÉXICO: '{lexema}' en línea {linea}, "  f"columna {columna} -> {motivo}")  print("\nRESULTADO: El archivo Dockerfile CONTIENE ERRORES LÉXICOS.")  else:  print("RESULTADO: El archivo Dockerfile es LÉXICAMENTE VÁLIDO "  "(no se encontraron caracteres o lexemas no reconocidos).")    print(f"\nTotal de tokens reconocidos: {len(tokens)}")  print(f"Total de errores léxicos: {len(errores)}")      def main():  if len(sys.argv) > 1:  ruta = sys.argv[1]  try:  with open(ruta, "r", encoding="utf-8") as f:  contenido = f.read()  except OSError as e:  print(f"Error al abrir el archivo '{ruta}': {e}")  sys.exit(1)  nombre = ruta  else:  contenido = sys.stdin.read()  nombre = "<stdin>"    tokens, errores = analizar(contenido)  imprimir\_resultado(tokens, errores, nombre)    # Código de salida: 0 si no hay errores léxicos, 1 si existen.  sys.exit(1 if errores else 0)      if \_\_name\_\_ == "\_\_main\_\_":  main() |

**Ejemplos de Ejecución**

Se ejecutó el lexer sobre tres archivos Dockerfile de prueba mediante el comando:

|  |
| --- |
| python3 src/lexer\_dockerfile.py ejemplos/<archivo>.dockerfile |

## 6.1. Ejemplo 1 - Dockerfile simple y válido

Archivo de entrada (ejemplo1\_valido\_simple.dockerfile):

|  |
| --- |
| # Ejemplo 1: Dockerfile simple y correcto para una app Python  FROM python:3.12-slim    LABEL maintainer="equipo-devops@empresa.com"    WORKDIR /app    COPY requirements.txt /app/requirements.txt  RUN pip install --no-cache-dir -r requirements.txt    COPY . /app    ENV PORT=8080  EXPOSE 8080/tcp    USER 1000    CMD ["python", "app.py"] |

Salida obtenida:

|  |
| --- |
| === Análisis léxico de: ejemplos/ejemplo1\_valido\_simple.dockerfile ===    TOKEN: INSTRUCTION Lexema: FROM (línea 2, columna 1)  TOKEN: IMAGE\_TAG Lexema: python:3.12-slim (línea 2, columna 6)  TOKEN: INSTRUCTION Lexema: LABEL (línea 4, columna 1)  TOKEN: ASSIGN Lexema: maintainer= (línea 4, columna 7)  TOKEN: STRING\_DOUBLE Lexema: "equipo-devops@empresa.com" (línea 4, columna 18)  TOKEN: INSTRUCTION Lexema: WORKDIR (línea 6, columna 1)  TOKEN: PATH Lexema: /app (línea 6, columna 9)  TOKEN: INSTRUCTION Lexema: COPY (línea 8, columna 1)  TOKEN: IDENTIFIER Lexema: requirements.txt (línea 8, columna 6)  TOKEN: PATH Lexema: /app/requirements.txt (línea 8, columna 23)  TOKEN: INSTRUCTION Lexema: RUN (línea 9, columna 1)  TOKEN: IDENTIFIER Lexema: pip (línea 9, columna 5)  TOKEN: IDENTIFIER Lexema: install (línea 9, columna 9)  TOKEN: FLAG Lexema: --no-cache-dir (línea 9, columna 17)  TOKEN: FLAG Lexema: -r (línea 9, columna 32)  TOKEN: IDENTIFIER Lexema: requirements.txt (línea 9, columna 35)  TOKEN: INSTRUCTION Lexema: COPY (línea 11, columna 1)  TOKEN: DOT\_PATH Lexema: . (línea 11, columna 6)  TOKEN: PATH Lexema: /app (línea 11, columna 8)  TOKEN: INSTRUCTION Lexema: ENV (línea 13, columna 1)  TOKEN: ASSIGN Lexema: PORT= (línea 13, columna 5)  TOKEN: NUMBER Lexema: 8080 (línea 13, columna 10)  TOKEN: INSTRUCTION Lexema: EXPOSE (línea 14, columna 1)  TOKEN: PORT Lexema: 8080/tcp (línea 14, columna 8)  TOKEN: INSTRUCTION Lexema: USER (línea 16, columna 1)  TOKEN: NUMBER Lexema: 1000 (línea 16, columna 6)  TOKEN: INSTRUCTION Lexema: CMD (línea 18, columna 1)  TOKEN: LBRACKET Lexema: [ (línea 18, columna 5)  TOKEN: STRING\_DOUBLE Lexema: "python" (línea 18, columna 6)  TOKEN: COMMA Lexema: , (línea 18, columna 14)  TOKEN: STRING\_DOUBLE Lexema: "app.py" (línea 18, columna 16)  TOKEN: RBRACKET Lexema: ] (línea 18, columna 24)    RESULTADO: El archivo Dockerfile es LÉXICAMENTE VÁLIDO (no se encontraron caracteres o lexemas no reconocidos).    Total de tokens reconocidos: 32  Total de errores léxicos: 0 |

Análisis: el lexer reconoció 32 tokens y 0 errores léxicos. Todas las instrucciones (FROM, LABEL, WORKDIR, COPY, RUN, ENV, EXPOSE, USER, CMD) fueron correctamente clasificadas como INSTRUCTION, la imagen base python:3.12-slim como IMAGE\_TAG, la bandera --no-cache-dir y la forma corta -r como FLAG, y el arreglo exec final se descompuso en LBRACKET, STRING\_DOUBLE, COMMA y RBRACKET. El programa concluye correctamente que el archivo es léxicamente válido.

## 6.2. Ejemplo 2 - Dockerfile multi-stage válido (con digest y banderas)

Archivo de entrada (ejemplo2\_valido\_multistage.dockerfile):

|  |
| --- |
| # Ejemplo 2: Dockerfile multi-stage, válido, con banderas y digest de imagen  FROM golang:1.22-alpine AS builder  WORKDIR /src  COPY go.mod go.sum ./  RUN go mod download  COPY . .  RUN go build -o /out/servidor ./cmd/servidor    FROM alpine@sha256:c158987ec3d3c9040c9d7b0f501a37b6e9d8c1a11cff96b5c8c5d8f37c96f6cc  RUN apk add --no-cache ca-certificates  COPY --from=builder /out/servidor /usr/local/bin/servidor  VOLUME ["/data"]  EXPOSE 9090/tcp  ARG BUILD\_VERSION=1.0.0  ENV APP\_ENV=production  ENTRYPOINT ["/usr/local/bin/servidor"] |

Salida obtenida:

|  |
| --- |
| === Análisis léxico de: ejemplos/ejemplo2\_valido\_multistage.dockerfile ===    TOKEN: INSTRUCTION Lexema: FROM (línea 2, columna 1)  TOKEN: IMAGE\_TAG Lexema: golang:1.22-alpine (línea 2, columna 6)  TOKEN: IDENTIFIER Lexema: AS (línea 2, columna 25)  TOKEN: IDENTIFIER Lexema: builder (línea 2, columna 28)  TOKEN: INSTRUCTION Lexema: WORKDIR (línea 3, columna 1)  TOKEN: PATH Lexema: /src (línea 3, columna 9)  TOKEN: INSTRUCTION Lexema: COPY (línea 4, columna 1)  TOKEN: IDENTIFIER Lexema: go.mod (línea 4, columna 6)  TOKEN: IDENTIFIER Lexema: go.sum (línea 4, columna 13)  TOKEN: DOT\_PATH Lexema: ./ (línea 4, columna 20)  TOKEN: INSTRUCTION Lexema: RUN (línea 5, columna 1)  TOKEN: IDENTIFIER Lexema: go (línea 5, columna 5)  TOKEN: IDENTIFIER Lexema: mod (línea 5, columna 8)  TOKEN: IDENTIFIER Lexema: download (línea 5, columna 12)  TOKEN: INSTRUCTION Lexema: COPY (línea 6, columna 1)  TOKEN: DOT\_PATH Lexema: . (línea 6, columna 6)  TOKEN: DOT\_PATH Lexema: . (línea 6, columna 8)  TOKEN: INSTRUCTION Lexema: RUN (línea 7, columna 1)  TOKEN: IDENTIFIER Lexema: go (línea 7, columna 5)  TOKEN: IDENTIFIER Lexema: build (línea 7, columna 8)  TOKEN: FLAG Lexema: -o (línea 7, columna 14)  TOKEN: PATH Lexema: /out/servidor (línea 7, columna 17)  TOKEN: DOT\_PATH Lexema: ./cmd/servidor (línea 7, columna 31)  TOKEN: INSTRUCTION Lexema: FROM (línea 9, columna 1)  TOKEN: IMAGE\_DIGEST Lexema: alpine@sha256:c158987ec3d3c9040c9d7b0f501a37b6e9d8c1a11cff96b5c8c5d8f37c96f6cc (línea 9, columna 6)  TOKEN: INSTRUCTION Lexema: RUN (línea 10, columna 1)  TOKEN: IDENTIFIER Lexema: apk (línea 10, columna 5)  TOKEN: IDENTIFIER Lexema: add (línea 10, columna 9)  TOKEN: FLAG Lexema: --no-cache (línea 10, columna 13)  TOKEN: IDENTIFIER Lexema: ca-certificates (línea 10, columna 24)  TOKEN: INSTRUCTION Lexema: COPY (línea 11, columna 1)  TOKEN: FLAG Lexema: --from=builder (línea 11, columna 6)  TOKEN: PATH Lexema: /out/servidor (línea 11, columna 21)  TOKEN: PATH Lexema: /usr/local/bin/servidor (línea 11, columna 35)  TOKEN: INSTRUCTION Lexema: VOLUME (línea 12, columna 1)  TOKEN: LBRACKET Lexema: [ (línea 12, columna 8)  TOKEN: STRING\_DOUBLE Lexema: "/data" (línea 12, columna 9)  TOKEN: RBRACKET Lexema: ] (línea 12, columna 16)  TOKEN: INSTRUCTION Lexema: EXPOSE (línea 13, columna 1)  TOKEN: PORT Lexema: 9090/tcp (línea 13, columna 8)  TOKEN: INSTRUCTION Lexema: ARG (línea 14, columna 1)  TOKEN: ASSIGN Lexema: BUILD\_VERSION= (línea 14, columna 5)  TOKEN: NUMBER Lexema: 1.0.0 (línea 14, columna 19)  TOKEN: INSTRUCTION Lexema: ENV (línea 15, columna 1)  TOKEN: ASSIGN Lexema: APP\_ENV= (línea 15, columna 5)  TOKEN: IDENTIFIER Lexema: production (línea 15, columna 13)  TOKEN: INSTRUCTION Lexema: ENTRYPOINT (línea 16, columna 1)  TOKEN: LBRACKET Lexema: [ (línea 16, columna 12)  TOKEN: STRING\_DOUBLE Lexema: "/usr/local/bin/servidor" (línea 16, columna 13)  TOKEN: RBRACKET Lexema: ] (línea 16, columna 38)    RESULTADO: El archivo Dockerfile es LÉXICAMENTE VÁLIDO (no se encontraron caracteres o lexemas no reconocidos).    Total de tokens reconocidos: 50  Total de errores léxicos: 0 |

Análisis: se reconocieron 50 tokens y 0 errores. Este ejemplo, más exigente, valida la correcta priorización de patrones: la imagen con digest alpine@sha256:... se identificó íntegramente como un único token IMAGE\_DIGEST (y no como IMAGE\_TAG truncado), la bandera de dos partes --from=builder se reconoció como un solo FLAG, y el número de versión 1.0.0 se tokenizó completo gracias al patrón NUMBER con soporte para notación decimal encadenada, en lugar de fragmentarse en tokens NUMBER y errores por cada punto.

## 6.3. Ejemplo 3 - Dockerfile con errores léxicos intencionales

Archivo de entrada (ejemplo3\_con\_errores.dockerfile):

|  |
| --- |
| # Ejemplo 3: Dockerfile con errores léxicos intencionales  FORM ubuntu:22.04    RUN echo "hola mundo" && apt-get update && apt-get install -y curl    ENV RUTA=$RUTA:/usr/local/bin    LABEL vers~ion="1.0"    EXPOSE 80!81    CMD ["python", "app.py"] |

Salida obtenida:

|  |
| --- |
| === Análisis léxico de: ejemplos/ejemplo3\_con\_errores.dockerfile ===    TOKEN: IMAGE\_TAG Lexema: ubuntu:22.04 (línea 2, columna 6)  TOKEN: INSTRUCTION Lexema: RUN (línea 4, columna 1)  TOKEN: IDENTIFIER Lexema: echo (línea 4, columna 5)  TOKEN: STRING\_DOUBLE Lexema: "hola mundo" (línea 4, columna 10)  TOKEN: AND\_OP Lexema: && (línea 4, columna 23)  TOKEN: IDENTIFIER Lexema: apt-get (línea 4, columna 26)  TOKEN: IDENTIFIER Lexema: update (línea 4, columna 34)  TOKEN: AND\_OP Lexema: && (línea 4, columna 41)  TOKEN: IDENTIFIER Lexema: apt-get (línea 4, columna 44)  TOKEN: IDENTIFIER Lexema: install (línea 4, columna 52)  TOKEN: FLAG Lexema: -y (línea 4, columna 60)  TOKEN: IDENTIFIER Lexema: curl (línea 4, columna 63)  TOKEN: INSTRUCTION Lexema: ENV (línea 6, columna 1)  TOKEN: ASSIGN Lexema: RUTA= (línea 6, columna 5)  TOKEN: VARIABLE Lexema: $RUTA (línea 6, columna 10)  TOKEN: PATH Lexema: /usr/local/bin (línea 6, columna 16)  TOKEN: INSTRUCTION Lexema: LABEL (línea 8, columna 1)  TOKEN: IDENTIFIER Lexema: vers (línea 8, columna 7)  TOKEN: ASSIGN Lexema: ion= (línea 8, columna 12)  TOKEN: STRING\_DOUBLE Lexema: "1.0" (línea 8, columna 16)  TOKEN: INSTRUCTION Lexema: EXPOSE (línea 10, columna 1)  TOKEN: NUMBER Lexema: 80 (línea 10, columna 8)  TOKEN: NUMBER Lexema: 81 (línea 10, columna 11)  TOKEN: INSTRUCTION Lexema: CMD (línea 12, columna 1)  TOKEN: LBRACKET Lexema: [ (línea 12, columna 5)  TOKEN: STRING\_DOUBLE Lexema: "python" (línea 12, columna 6)  TOKEN: COMMA Lexema: , (línea 12, columna 14)  TOKEN: STRING\_DOUBLE Lexema: "app.py" (línea 12, columna 16)  TOKEN: RBRACKET Lexema: ] (línea 12, columna 24)    --- Se encontraron 4 error(es) léxico(s) ---  ERROR LÉXICO: 'FORM' en línea 2, columna 1 -> instrucción Docker no reconocida (¿error de escritura?)  ERROR LÉXICO: ':' en línea 6, columna 15 -> carácter no reconocido por el alfabeto del lenguaje  ERROR LÉXICO: '~' en línea 8, columna 11 -> carácter no reconocido por el alfabeto del lenguaje  ERROR LÉXICO: '!' en línea 10, columna 10 -> carácter no reconocido por el alfabeto del lenguaje    RESULTADO: El archivo Dockerfile CONTIENE ERRORES LÉXICOS.    Total de tokens reconocidos: 29  Total de errores léxicos: 4 |

Análisis: el lexer detectó 4 errores léxicos sin detener la ejecución (estado fallido con retorno automático al estado inicial): (1) FORM en la línea 2 fue reportado como instrucción Docker no reconocida (probable error de escritura de FROM); (2) el carácter ':' sobrante en la línea 6 (RUTA=$RUTA:/usr/local/bin, un caso donde la variable expandida seguida de dos puntos no corresponde a ningún patrón definido); (3) el carácter '~' en la línea 8 dentro de vers~ion="1.0"; y (4) el carácter '!' en la línea 10 dentro de 80!81. En cada caso se indica la línea y columna exacta, permitiendo ubicar el error rápidamente en el archivo. El programa concluye correctamente que el archivo NO es léxicamente válido, y retorna código de salida 1.

**Conclusiones**

* Se comprobó en la práctica que un conjunto de expresiones regulares combinadas mediante alternancia con grupos con nombre es una representación compacta y funcional de un autómata finito determinístico para el análisis léxico, sin necesidad de codificar manualmente la tabla de transiciones de estados.
* El orden de las alternativas dentro de la expresión regular combinada es crítico: resuelve, de forma equivalente a como se resolvería en el diseño manual de un AFD, los conflictos entre patrones que podrían coincidir sobre la misma entrada (por ejemplo, imagen:tag frente a puerto:puerto).
* El manejo de errores mediante un token MISMATCH (estado fallido) que reinicia el análisis en el estado inicial, en lugar de detener la ejecución al primer error, permite reportar todos los errores léxicos de un archivo en una sola pasada, resultado directamente útil para una herramienta real de verificación de Dockerfiles.
* El lexer desarrollado cumple el objetivo de la actividad: dado un archivo Docker P, informa si P es léxicamente válido o señala, con línea y columna, cada error léxico encontrado.