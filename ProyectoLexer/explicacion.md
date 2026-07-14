# Analizador Léxico para Lenguaje L (Subconjunto de Rust)

## 1. Manual de Usuario del Metacompilador (Flex)
Flex es una herramienta de metacompilación que transforma descripciones de patrones léxicos (expresiones regulares) en un programa ejecutable en lenguaje C. Su flujo de trabajo consiste en tres secciones:
- **Definiciones:** Donde se incluyen librerías y configuraciones.
- **Reglas:** Sección principal donde se vinculan expresiones regulares con acciones (como imprimir el token encontrado).
- **Código de Usuario:** Contiene la función principal `main` y la lógica de control.

## 2. Descripción del Lenguaje L
L es un subconjunto de Rust diseñado para fines educativos, soportando:
- **Palabras reservadas:** `let`, `mut`, `fn`.
- **Tipos y valores:** `i32`, booleanos (`true`, `false`) y números enteros.
- **Estructuras:** Identificadores de variables y operadores básicos (`=`, `+`, `;`)[cite: 1].

## 3. Documentación del Proceso de Creación
### Pasos de Instalación e Implementación
1. **Entorno:** Se utilizó WSL (Ubuntu) sobre Windows para asegurar compatibilidad con herramientas nativas de compilación[cite: 1].
2. **Instalación:** Se ejecutó `sudo apt install flex gcc build-essential`[cite: 1].
3. **Generación:** Se transformó la especificación con el comando `flex rust_lexer.l` para generar `lex.yy.c`[cite: 1].
4. **Compilación:** Se obtuvo el ejecutable con `gcc lex.yy.c -o rust_lexer`[cite: 1].
5. **Ejecución:** Se procesa el código fuente con `./rust_lexer prueba.rs`[cite: 1].