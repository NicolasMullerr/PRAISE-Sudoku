import time
import random
import os
from environments import SimulatedEnvironment, SimulatedSensor, SimulatedActuator



class EntornoSudoku(SimulatedEnvironment):

    def __init__(self, tablero_inicial=None):
        super().__init__()
        self.tablero = [[0 for _ in range(9)] for _ in range(9)]  # Initialize a 9x9 Sudoku grid with zeros
        self.posiciones_confirmadas = []  # Initialize an empty list to store confirmed positions
        self.posiciones_borrador = []  # Initialize an empty list to store draft positions
        self.dificultad = "Extrema"  # Initialize difficulty to "Extrema"
        self.vidas = 3  # Initialize lives to 3
        self.pistas = 17  # Initialize hints to 17
        self.posiciones_pistas = [] # Initialize an empty list to store hint positions
        self.tiempo_penalizacion = 30 # Initialize time penalty to 30 seconds
        self.total_tiempo_penalizacion = 0 # Initialize the total time penalty to 0 seconds
        if tablero_inicial is not None:
            self._cargar_tablero(tablero_inicial)
        else:
            self._generar_pistas_iniciales() # Call the method to generate initial hints
        self.tiempo_inicio = time.time() # Store the start time of the game

    def _cargar_tablero(self, fuente):
        """Carga un tablero inicial desde una ruta de archivo (.txt), un string de 81 caracteres o una matriz 9x9."""
        contenido = ""
        if isinstance(fuente, str) and (os.path.isfile(fuente) or fuente.strip().endswith('.txt')):
            with open(fuente, 'r', encoding='utf-8') as f:
                contenido = f.read()
        elif isinstance(fuente, str):
            contenido = fuente
        elif isinstance(fuente, (list, tuple)):
            if len(fuente) == 9 and all(len(fila) == 9 for fila in fuente):
                self.tablero = [[int(fuente[r][c]) for c in range(9)] for r in range(9)]
                self.posiciones_pistas = [(f, c) for f in range(9) for c in range(9) if self.tablero[f][c] != 0]
                self.pistas = len(self.posiciones_pistas)
                return
            else:
                raise ValueError("La matriz suministrada debe ser de tamaño 9x9.")
        else:
            raise TypeError("El tablero inicial debe ser una ruta de archivo, una cadena de caracteres o una matriz 9x9.")

        # Extraemos los primeros 81 dígitos (admitiendo '.' como 0)
        digitos = []
        for ch in contenido:
            if ch.isdigit():
                digitos.append(int(ch))
            elif ch == '.':
                digitos.append(0)
            if len(digitos) == 81:
                break

        if len(digitos) != 81:
            raise ValueError(f"Se esperaban 81 dígitos para el tablero de Sudoku, pero se encontraron {len(digitos)}.")

        self.tablero = [digitos[i * 9:(i + 1) * 9] for i in range(9)]
        self.posiciones_pistas = [(f, c) for f in range(9) for c in range(9) if self.tablero[f][c] != 0]
        self.pistas = len(self.posiciones_pistas)


    def _generar_pistas_iniciales(self):   # Hay que ver si se puede hacer mas realista, pero por ahora funciona.
        # 1. Llenamos el tablero completamente usando Backtracking
        self._resolver_tablero_backtracking()
        
        # 2. Elegimos 17 posiciones al azar del tablero resuelto
        todas_las_coordenadas = [(f, c) for f in range(9) for c in range(9)]
        self.posiciones_pistas = random.sample(todas_las_coordenadas, self.pistas)
        
        # 3. Vaciamos todo lo que NO sea una pista
        for f in range(9):
            for c in range(9):
                if (f, c) not in self.posiciones_pistas:
                    self.tablero[f][c] = 0

    def _es_valido_generacion(self, fila, columna, numero):
        # Una función rápida (sin usar las listas del agente) para validar 
        # si un número se puede poner durante la generación del tablero.
        for i in range(9):
            if self.tablero[fila][i] == numero or self.tablero[i][columna] == numero: #Fija primero fila y luego columna para ver si esta el numero
                return False #Si ya esta el numero en la fila o columna, no es valido
                
        f_reg, c_reg = (fila // 3) * 3, (columna // 3) * 3 #Para calcular dónde empieza el cuadrante de 3x3 al que pertenece la celda (// Div entera)
        for i in range(3): # Recorremos las 3 filas y 3 columnas del cuadrante buscando el numero
            for j in range(3):
                if self.tablero[f_reg + i][c_reg + j] == numero:
                    return False #Si ya esta el numero en el cuadrante, no es valido
        return True

    def _resolver_tablero_backtracking(self):
        # Buscamos la primera celda vacía
        for fila in range(9):
            for columna in range(9):
                if self.tablero[fila][columna] == 0:
                    
                    # Probamos los números del 1 al 9 mezclados al azar
                    numeros = list(range(1, 10))
                    random.shuffle(numeros)
                    
                    for numero in numeros:
                        if self._es_valido_generacion(fila, columna, numero):
                            self.tablero[fila][columna] = numero
                            
                            # Llamada RECURSIVA: intentamos resolver el resto
                            if self._resolver_tablero_backtracking():
                                return True
                                
                            # Si no se pudo resolver, deshacemos (Backtrack)
                            self.tablero[fila][columna] = 0
                            
                    return False # Si ningún número funcionó, hay que volver atrás
        return True # Si no hay celdas vacías, ¡el tablero está resuelto!


    # --- REGLAS DE UNICIDAD ---
    
    def _falla_unicidad_fila(self, fila, numero):
        # Creamos una lista temporal que SOLO guarda los números de esa fila
        # si su coordenada (fila, c) existe en tus listas de posiciones oficiales.
        numeros_oficiales_en_fila = [
            self.tablero[fila][c] for c in range(9) 
            if (fila, c) in self.posiciones_confirmadas or (fila, c) in self.posiciones_pistas
        ]
        # Usamos count() para ver cuantos números oficiales hay en esa fila que sean iguales al número que queremos colocar.
        if numeros_oficiales_en_fila.count(numero) > 0:
            return True # Hay infracción
            
        return False # Pasó la prueba
    

    def _verificar_unicidad_columna(self, columna, numero):
        # Creamos una lista temporal que SOLO guarda los números de esa columna
        # si su coordenada (fila, c) existe en tus listas de posiciones oficiales.
        numeros_oficiales_en_columna = [
            self.tablero[f][columna] for f in range(9) 
            if (f, columna) in self.posiciones_confirmadas or (f, columna) in self.posiciones_pistas
        ]
        # Usamos count() para ver cuantos números oficiales hay en esa columna que sean iguales al número que queremos colocar.
        if numeros_oficiales_en_columna.count(numero) > 0:
            return True # Hay infracción
            
        return False # Pasó la prueba

    def _verificar_unicidad_region(self, fila, columna, numero):
        # Calculamos la fila y columna de la región 3x3 a la que pertenece la celda (fila, columna)
        fila_region = (fila // 3) * 3
        columna_region = (columna // 3) * 3

        # Creamos una lista temporal que SOLO guarda los números de esa región
        # si su coordenada (f, c) existe en tus listas de posiciones oficiales.
        numeros_oficiales_en_region = [
            self.tablero[f][c] for f in range(fila_region, fila_region + 3) 
            for c in range(columna_region, columna_region + 3)
            if (f, c) in self.posiciones_confirmadas or (f, c) in self.posiciones_pistas
        ]
        # Usamos count() para ver cuantos números oficiales hay en esa región que sean iguales al número que queremos colocar.
        if numeros_oficiales_en_region.count(numero) > 0:
            return True # Hay infracción
            
        return False # Pasó la prueba
    # ------

    def get_property(self, agent_id: int, property_name: str) -> dict:
        """
        Sensor del entorno. El agente pide una propiedad por su nombre.
        """
        if agent_id not in self._agents:
            return {} # Agente no registrado

        match property_name:
            case "tablero":
                return {"tablero": self.tablero}
            case "vidas":
                return {"vidas": self.vidas}
            case "penalizacion":
                return {"tiempo_penalizado": self.total_tiempo_penalizacion}
            case "tiempo_total":
                # 1. Calculamos el tiempo real de procesamiento
                tiempo_real_transcurrido = time.time() - self.tiempo_inicio
                # 2. Le sumamos los castigos acumulados
                tiempo_total = tiempo_real_transcurrido + self.total_tiempo_penalizacion
                return {"tiempo_total": tiempo_total}
            case "estado_celda":
                return {
                    "confirmadas": self.posiciones_confirmadas,
                    "borradores": self.posiciones_borrador,
                    "pistas": self.posiciones_pistas
                }
            case _:
                return {} # Retorna diccionario vacío si pide algo que no existe

    def take_action(self, agent_id: int, action_name: str, params: dict = {}) -> None:
        """
        Actuador del entorno. Ejecuta acciones basadas en el nombre y los parámetros.
        """
        if agent_id not in self._agents:
            return # Agente no registrado

        # Extraemos los parámetros de forma segura (soportando tanto 'numero' como 'valor')
        fila = params.get("fila")
        columna = params.get("columna")
        numero = params.get("numero") if params.get("numero") is not None else params.get("valor")
        coordenada = (fila, columna)

        # Si alguna coordenada es None, evitamos que el código falle y simplemente retornamos sin hacer nada.
        if fila is None or columna is None:
            return

        # ENRUTAMIENTO DE ACCIONES
        match action_name:
            case "escribir":
                # Guardamos solo la tupla de la coordenada en la lista de borradores si no está ya
                if coordenada not in self.posiciones_borrador and coordenada not in self.posiciones_confirmadas and coordenada not in self.posiciones_pistas:
                    self.posiciones_borrador.append(coordenada)
                    # El número real va a la matriz matemática
                    self.tablero[fila][columna] = numero

            case "confirmar":
                # 1. Verificamos que la celda sea un borrador antes de hacer nada
                if coordenada in self.posiciones_borrador:

                    # 2. Ejecutamos las validaciones
                    falla_fila = self._falla_unicidad_fila(fila, numero)
                    falla_col = self._verificar_unicidad_columna(columna, numero)
                    falla_reg = self._verificar_unicidad_region(fila, columna, numero)

                    # 3. Si NO hay fallas (todas son False), validamos el número
                    if not falla_fila and not falla_col and not falla_reg:
                        self.posiciones_borrador.remove(coordenada)
                        self.posiciones_confirmadas.append(coordenada)

                    # 4. Si ALGUNA regla falló, aplicamos el castigo y limpiamos la celda
                    else:
                        self.vidas -= 1
                        self.total_tiempo_penalizacion += self.tiempo_penalizacion
                        self.posiciones_borrador.remove(coordenada)
                        self.tablero[fila][columna] = 0

            case "borrar":
                # Las pistas son intocables: solo borramos si la celda NO es una pista
                if coordenada not in self.posiciones_pistas:
                    if coordenada in self.posiciones_borrador:
                        self.posiciones_borrador.remove(coordenada)
                    if coordenada in self.posiciones_confirmadas:
                        self.posiciones_confirmadas.remove(coordenada)
                    self.tablero[fila][columna] = 0  # Reiniciamos la celda a cero


# PRUEBA HARDCODE DEL ENTORNO SUDOKU

if __name__ == "__main__":
    
    print("--- INICIANDO BANCO DE PRUEBAS ---")
    
    # 1. Instanciamos el entorno (Acá se ejecuta el __init__ y el backtracking)
    mi_entorno = EntornoSudoku()
    
    # 2. Probamos el Sensor: Pedimos el tablero inicial
    tablero_inicial = mi_entorno.get_property(agent_id=1, property_name="tablero")["tablero"]
    
    print("\nTablero Generado (17 pistas):")
    for fila in tablero_inicial:
        print(fila)
        
 # 3. Probamos el Actuador: Acción Escribir (Forzando un error)
    print("\nSimulando Agente: Escribiendo un 2 en la coordenada (0, 0)...")
    mi_entorno.take_action(agent_id=1, action_name="escribir", params={"fila": 0, "columna": 0, "numero": 2})
    
    # 4. Verificamos los estados internos
    estados = mi_entorno.get_property(agent_id=1, property_name="estado_celda")
    print("Borradores actuales:", estados["borradores"])
    
    # 5. Probamos la Confirmación y el Castigo
    print("\nSimulando Agente: Confirmando la coordenada (0, 0)...")
    mi_entorno.take_action(agent_id=1, action_name="confirmar", params={"fila": 0, "columna": 0, "numero": 2})
    
    # Verificamos los castigos
    vidas_restantes = mi_entorno.get_property(agent_id=1, property_name="vidas")["vidas"]
    penalizacion = mi_entorno.get_property(agent_id=1, property_name="penalizacion")["tiempo_penalizado"]
    
# Pedimos el reporte de tiempo al final de la jugada
    reporte_tiempo = mi_entorno.get_property(agent_id=1, property_name="tiempo_total")
    
    print(f"\n--- REPORTE DE TIEMPO ---")
    print(f"TIEMPO TOTAL DEL JUEGO: {reporte_tiempo['tiempo_total']:.2f} segundos")
    print(f"TIEMPO DE CASTIGO: {penalizacion} segundos")
    print(f"Vidas restantes: {vidas_restantes}")