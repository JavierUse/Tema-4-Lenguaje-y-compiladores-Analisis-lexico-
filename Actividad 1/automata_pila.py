class AutomataDePila:
    """
    Clase que simula un Autómata de Pila básico.
    Este ejemplo está configurado para reconocer el lenguaje L = {a^n b^n | n >= 0}
    es decir, cadenas con una cantidad 'n' de 'a' seguidas de la misma cantidad de 'b'.
    """
    
    def __init__(self):
        self.pila = []
        # Símbolo inicial de la pila para identificar cuándo está vacía
        self.simbolo_inicial = 'Z0' 
        self.estado_actual = 'q0'
        
    def procesar_cadena(self, cadena):
        """
        Procesa una cadena de entrada.
        Retorna True si la cadena es aceptada, False en caso contrario.
        """
        # Reiniciamos el estado y la pila para cada nueva cadena
        self.pila = [self.simbolo_inicial]
        self.estado_actual = 'q0'
        
        print(f"\nProcesando cadena: '{cadena}'")
        
        for caracter in cadena:
            # Estado q0: Leyendo 'a's
            if self.estado_actual == 'q0':
                if caracter == 'a':
                    self.pila.append('A') # Apilamos una 'A' por cada 'a'
                    print(f"Leído 'a' -> Apila 'A'. Pila actual: {self.pila}")
                elif caracter == 'b':
                    # Transición al estado q1 al encontrar la primera 'b'
                    self.estado_actual = 'q1'
                    
                    # Verificamos si podemos desapilar
                    if self.pila[-1] == 'A':
                        self.pila.pop()
                        print(f"Leído 'b' -> Desapila 'A'. Pila actual: {self.pila}")
                    else:
                        print("Error: Se encontró 'b' pero no hay 'A' para desapilar.")
                        return False
                else:
                    print(f"Error: Carácter inválido '{caracter}'. Solo se permiten 'a' y 'b'.")
                    return False
                    
            # Estado q1: Leyendo 'b's
            elif self.estado_actual == 'q1':
                if caracter == 'b':
                    if self.pila[-1] == 'A':
                        self.pila.pop() # Desapilamos una 'A' por cada 'b'
                        print(f"Leído 'b' -> Desapila 'A'. Pila actual: {self.pila}")
                    else:
                        print("Error: Demasiadas 'b's, no quedan 'A's en la pila.")
                        return False
                elif caracter == 'a':
                    print("Error: Se encontró una 'a' después de una 'b'. El orden debe ser a^n b^n.")
                    return False
                else:
                    print(f"Error: Carácter inválido '{caracter}'.")
                    return False

        # Al terminar de leer la cadena, verificamos si la pila solo contiene el símbolo inicial
        if self.pila == [self.simbolo_inicial]:
            print("Resultado: CADENA ACEPTADA (La pila está vacía/en su estado inicial).")
            return True
        else:
            print("Resultado: CADENA RECHAZADA (Sobran elementos en la pila, más 'a's que 'b's).")
            return False

# Pruebas (Código fuente y compilable requerido)
if __name__ == "__main__":
    ap = AutomataDePila()
    
    # Casos de prueba válidos
    ap.procesar_cadena("")        # n=0
    ap.procesar_cadena("ab")      # n=1
    ap.procesar_cadena("aabb")    # n=2
    ap.procesar_cadena("aaabbb")  # n=3
    
    # Casos de prueba inválidos
    ap.procesar_cadena("a")       # Falta b
    ap.procesar_cadena("b")       # Falta a
    ap.procesar_cadena("aab")     # Más a que b
    ap.procesar_cadena("abb")     # Más b que a
    ap.procesar_cadena("aba")     # Orden incorrecto
