import agents
import time
import random
from abc import ABCMeta, abstractmethod


class SimulatedEnvironment(metaclass=ABCMeta):

    def __init__(self):
        self._agents = []
        self._statebuffers = []

    def add(self, agent_id: int) -> None:
        self._agents.append(agent_id)

    def remove(self, agent_id: int) -> None:
        if agent_id in self._agents:
            self._agents.remove(agent_id)

    def add_statebuffer(self, agent_id: int, statebuffer) -> None:
        self._agents.append(agent_id)
        self._statebuffers.append({"agent_id": agent_id, "statebuffer": statebuffer})

    def remove_statebuffer(self, agent_id: int, statebuffer) -> None:
        if agent_id in self._agents:
            self._agents.remove(agent_id)
            self._statebuffers.remove(statebuffer)

    @abstractmethod
    def get_property(self, agent_id: int, property_name: str) -> dict:
        pass

    @abstractmethod
    def take_action(self, agent_id: int, action_name: str, params: dict = {}) -> None:
        pass


class SimulatedSensor(agents.Sensor):

    def __init__(self, e: SimulatedEnvironment):
        self._agent = None
        self._env = e

    @property
    def agent(self):
        return self._agent

    @agent.setter
    def agent(self, a: agents.Agent):
        self._agent = a


class SimulatedActuator(agents.Actuator):

    def __init__(self, e: SimulatedEnvironment):
        self._env = e
        self._agent = None

    @property
    def agent(self):
        return self._agent

    @agent.setter
    def agent(self, a: agents.Agent):
        self._agent = a



class EntornoSudoku(SimulatedEnvironment):

    def __init__(self):
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
        self._generar_pistas_iniciales() # Call the method to generate initial hints
        self.tiempo_inicio = time.time() # Store the start time of the game


    def _generar_pistas_iniciales(self):
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
            if self.tablero[fila][i] == numero or self.tablero[i][columna] == numero:
                return False
                
        f_reg, c_reg = (fila // 3) * 3, (columna // 3) * 3
        for i in range(3):
            for j in range(3):
                if self.tablero[f_reg + i][c_reg + j] == numero:
                    return False
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
        if property_name == "tablero":
            return {"tablero": self.tablero}
            
        elif property_name == "vidas":
            return {"vidas": self.vidas}
            
        elif property_name == "penalizacion":
            return {"tiempo_penalizado": self.total_tiempo_penalizacion}
        
        elif property_name == "tiempo_total":
            # 1. Calculamos el tiempo real de procesamiento
            tiempo_real_transcurrido = time.time() - self.tiempo_inicio
            
            # 2. Le sumamos los castigos acumulados
            tiempo_total = tiempo_real_transcurrido + self.total_tiempo_penalizacion
            return {"tiempo_total": tiempo_total}
            
        elif property_name == "estado_celda":
            # Si necesitas que el agente consulte una celda específica, 
            # podrías requerir que mande coordenadas, pero por ahora 
            # con devolver el tablero completo y las listas suele bastar.
            return {
                "confirmadas": self.posiciones_confirmadas,
                "borradores": self.posiciones_borrador,
                "pistas": self.posiciones_pistas
            }
            
        return {} # Retorna diccionario vacío si pide algo que no existe

    def take_action(self, agent_id: int, action_name: str, params: dict = {}) -> None:
        """
        Actuador del entorno. Ejecuta acciones basadas en el nombre y los parámetros.
        """
        # Extraemos los parámetros de forma segura
        fila = params.get("fila")
        columna = params.get("columna")
        numero = params.get("numero")
        coordenada = (fila, columna)

        # Si alguna coordenada es None, evitamos que el código falle y simplemente retornamos sin hacer nada.
        if fila is None or columna is None:
            return

        # ENRUTAMIENTO DE ACCIONES
        if action_name == "escribir":
            # Guardamos solo la tupla de la coordenada en la lista de borradores
            self.posiciones_borrador.append(coordenada)
            # El número real va a la matriz matemática
            self.tablero[fila][columna] = numero

        elif action_name == "confirmar":
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
                    # Nota: No hace falta volver a poner el número en self.tablero 
                    # porque ya lo pusimos en la acción "escribir".
                    
                # 4. Si ALGUNA regla falló, aplicamos el castigo
                else:
                    self.vidas -= 1
                    self.total_tiempo_penalizacion += self.tiempo_penalizacion

        elif action_name == "borrar":
            # Borramos la celda de borradores y la ponemos en cero en el tablero
            if coordenada in self.posiciones_borrador:
                self.posiciones_borrador.remove(coordenada)
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