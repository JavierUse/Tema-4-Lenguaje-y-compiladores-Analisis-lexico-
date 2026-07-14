# Informe Teórico: Autómatas de Pila

## 1. Definición de Autómata de Pila (AP)

Un **Autómata de Pila** (Pushdown Automaton o PDA por sus siglas en inglés) es un modelo computacional que extiende la capacidad de los Autómatas Finitos (tanto Deterministas como No Deterministas) mediante la incorporación de una memoria adicional estructurada en forma de **pila** (stack). 

Mientras que un autómata finito solo tiene una cantidad finita de memoria en forma de estados, un autómata de pila posee una memoria infinita de tipo LIFO (Last-In, First-Out; el último en entrar es el primero en salir). Esto le permite procesar y recordar secuencias complejas, ya que puede "apilar" (push) símbolos en la memoria y "desapilar" (pop) símbolos cuando sea necesario según las reglas de transición.

Formalmente, un Autómata de Pila se define como una 7-tupla M = (Q, Σ, Γ, δ, q0, Z0, F), donde:
*   Q: Conjunto finito de estados.
*   Σ (Sigma): Alfabeto de entrada (símbolos que puede leer).
*   Γ (Gamma): Alfabeto de la pila (símbolos que puede guardar en la pila).
*   δ (Delta): Función de transición (determina el siguiente estado y la acción en la pila en base al estado actual, el símbolo leído y el símbolo en el tope de la pila).
*   q0 ∈ Q: Estado inicial.
*   Z0 ∈ Γ: Símbolo inicial de la pila (usado para saber cuándo la pila está vacía).
*   F ⊆ Q: Conjunto de estados finales o de aceptación.

## 2. Ejemplos de Autómatas de Pila

### Ejemplo 1: El lenguaje L = { a^n b^n | n ≥ 0 }
Este lenguaje consiste en todas las cadenas que tienen un número "n" de letras 'a' seguidas exactamente por el mismo número "n" de letras 'b' (ej: nulo, ab, aabb, aaabbb). **Un autómata finito no puede resolver este problema** porque no tiene memoria para contar cuántas 'a' han pasado. Un autómata de pila lo resuelve de la siguiente manera:
1.  Por cada 'a' que lee en la entrada, apila un símbolo (ej. 'A') en la pila.
2.  Cuando empieza a leer las 'b', por cada 'b' desapila una 'A'.
3.  Si al terminar de leer la cadena, la pila queda vacía (es decir, solo queda el símbolo inicial $Z_0$), significa que hubo la misma cantidad de 'a' y de 'b', por lo que acepta la cadena. Si sobran 'A' en la pila, o faltan 'A' para emparejar con las 'b', rechaza la cadena.

### Ejemplo 2: Verificación de Paréntesis Balanceados
Lenguajes de programación y expresiones matemáticas requieren que los paréntesis estén correctamente cerrados (ej: `(())()`, `(()())`).
1.  El autómata lee la expresión de izquierda a derecha.
2.  Al leer un paréntesis de apertura `(`, lo apila.
3.  Al leer un paréntesis de cierre `)`, desapila un elemento del tope de la pila. Si el tope de la pila no es un `(`, o si la pila está vacía antes de tiempo, la expresión está desbalanceada (rechazo).
4.  Si al terminar de leer la cadena la pila está vacía, los paréntesis estaban perfectamente balanceados.

---

## 3. Conclusión de las Utilidades del Autómata de Pila

Los autómatas de pila tienen utilidades prácticas fundamentales en el campo de la informática y el desarrollo de software. Su utilidad principal radica en el **análisis sintáctico (Parsing)**. 

Son la base teórica de los lenguajes libres de contexto. En la construcción de **compiladores e intérpretes**, las herramientas que analizan la sintaxis del código fuente (parsers) están implementadas utilizando principios de autómatas de pila. Por ejemplo, se utilizan para evaluar expresiones aritméticas con prioridades de operadores, validar que los bloques de código como `if`, `while`, o `{}` estén correctamente estructurados y anidados, y procesar formatos de datos jerárquicos como XML o HTML. Sin la estructura LIFO de una pila, las computadoras no podrían procesar lenguajes con estructuras recursivas y anidadas.

---

## 4. Importancia Relacionada a su Poder con Relación a los AFD y AFND

La importancia del Autómata de Pila se entiende mejor al compararlo con los Autómatas Finitos Deterministas (AFD) y No Deterministas (AFND).

*   **Poder Computacional:** Los Autómatas de Pila son **estrictamente más poderosos** que los AFD y los AFND.
*   **Lenguajes que reconocen:** Mientras que los AFD y AFND solo pueden reconocer **Lenguajes Regulares** (aquellos que pueden ser descritos mediante expresiones regulares, donde no se requiere memoria para "contar" o emparejar de forma arbitraria), los Autómatas de Pila pueden reconocer **Lenguajes Libres de Contexto (LLC)**.
*   **La Limitación de los AFD/AFND:** Un AFD/AFND no puede recordar cantidades arbitrarias de información. Por ejemplo, no puede recordar si vio $n$ cantidades de 'a' para luego exigir $n$ cantidades de 'b', porque requeriría infinitos estados para representar cada valor posible de $n$.
*   **El Salto Cualitativo del AP:** La adición de la pila provee memoria infinita controlada. Esto permite resolver problemas de emparejamiento, recursividad y anidamiento. Todo lenguaje regular puede ser reconocido por un autómata de pila (simplemente ignorando la pila), pero no todo lenguaje libre de contexto puede ser reconocido por un AFD/AFND. Por lo tanto, el AP representa el siguiente nivel en la Jerarquía de Chomsky, siendo indispensable para definir los lenguajes de programación modernos que poseen reglas sintácticas complejas.

---

## 5. Documentación de la Solución de Software

Como parte de esta actividad, se ha construido un programa que simula un Autómata de Pila básico. A continuación, se detallan los aspectos técnicos de esta solución, cumpliendo con los requerimientos de la entrega:

### Descripción del Programa
El programa construido (`automata_pila.py`) implementa la clase `AutomataDePila` configurada específicamente para reconocer el lenguaje $L = \{a^n b^n \mid n \ge 0\}$.
Este script simula las transiciones de estado y las operaciones de memoria (apilar y desapilar) carácter por carácter. Incluye un método `procesar_cadena(cadena)` que determina si una cadena dada es aceptada o rechazada, imprimiendo en consola el paso a paso del procesamiento, el estado de la pila y el veredicto final.

### Tecnología y Herramientas Utilizadas
*   **Lenguaje de Programación:** Python 3.x
*   **Paradigma:** Programación Orientada a Objetos (POO). Se encapsuló la lógica y los datos (estado actual, pila) en una clase.
*   **Herramientas:** Cualquier editor de código (VS Code, Sublime Text, etc.) y la terminal/consola del sistema operativo para la ejecución. No se requirieron librerías de terceros.

### Detalle de Instalación
Dado que el programa es un script de Python estándar utilizando únicamente la biblioteca estándar, no requiere de una instalación compleja ni gestión de dependencias externas.
Los pasos previos son:
1.  Verificar que se tiene instalado **Python 3** en el sistema. Se puede descargar desde la [página oficial de Python](https://www.python.org/downloads/).
2.  Descargar o clonar el archivo `automata_pila.py` del repositorio entregado.

### Detalle de Ejecución
Para probar y ejecutar el simulador del autómata de pila, se deben seguir estos pasos:
1.  Abra una terminal o línea de comandos (Símbolo del sistema, PowerShell, Git Bash, etc.).
2.  Navegue utilizando el comando `cd` hasta el directorio donde se encuentra guardado el archivo `automata_pila.py`.
3.  Ejecute el script escribiendo el siguiente comando:
    ```bash
    python automata_pila.py
    ```
4.  Al ejecutarse, el programa correrá automáticamente el bloque de pruebas definido al final del archivo. Este evaluará una serie de casos de prueba válidos (ej. `"aabb"`) e inválidos (ej. `"abb"`), mostrando por consola cada símbolo leído, la acción sobre la pila y si la cadena fue **ACEPTADA** o **RECHAZADA**.
