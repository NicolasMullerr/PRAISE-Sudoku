from environments import SimulatedSensor, SimulatedActuator, SimulatedEnvironment
from agents import Agent
from random import randrange

# Primeramente definimos los sensores para el agente del juego de Sudoku

class TableroSensor(SimulatedSensor):

    def sense(self):
        response = self._env.get_property(self._agent.id, property_name="tablero")
        return response["tablero"]
    
class VidasSensor(SimulatedSensor):

    def sense(self):
        response = self._env.get_property(self._agent.id, property_name="vidas")
        return response["vidas"]
    
class PenalizacionSensor(SimulatedSensor):

    def sense(self):
        response = self._env.get_property(self._agent.id, property_name="penalizacion")
        return response["tiempo_penalizado"]

class Tiempo_totalSensor(SimulatedSensor):

    def sense(self):
        response = self._env.get_property(self._agent.id, property_name="tiempo_total")
        return response["tiempo_total"]    

class EstadoCeldaSensor(SimulatedSensor):

    def sense(self):
        response = self._env.get_property(self._agent.id, property_name="estado_celda")
        return response
    
# Ahora definimos los actuadores para el agente del juego de Sudoku

class EscribirActuator(SimulatedActuator):

    def act(self, fila: int, columna: int, valor: int):
        request_info = {"fila": fila, "columna": columna, "numero": valor}
        self._env.take_action(self._agent.id, "escribir", request_info)

class BorrarActuator(SimulatedActuator):

    def act(self, fila: int, columna: int):
        request_info = {"fila": fila, "columna": columna}
        self._env.take_action(self._agent.id, "borrar", request_info)

class ConfirmarActuator(SimulatedActuator):
    def act(self, fila: int, columna: int, valor: int):
        request_info = {"fila": fila, "columna": columna, "numero": valor}
        self._env.take_action(self._agent.id, "confirmar", request_info)

# Ahora definimos el agente del juego de Sudoku

class SudokuAgent(Agent):

    def _es_valido(self, tablero, fila, columna, numero):
        """El agente simula en su cabeza si el número choca con algo en el tablero visible."""
        # Revisar fila y columna
        for i in range(9):
            if tablero[fila][i] == numero or tablero[i][columna] == numero:
                return False
                
        # Revisar región 3x3
        f_reg, c_reg = (fila // 3) * 3, (columna // 3) * 3
        for i in range(3):
            for j in range(3):
                if tablero[f_reg + i][c_reg + j] == numero:
                    return False
        return True

    def function(self, percept):
        tablero = percept["tablero_sensor"]
        estado_celda = percept["estado_celda_sensor"]
        action = {}

        # PASO 1: Si chocamos con un callejón sin salida y hay que retroceder (Backtracking)
        if self.modo_retroceso:
            if not self.historial_movimientos:
                print("El tablero no tiene solución posible.")
                action["name"] = "esperar" 
                return action
            
            # Sacamos el último movimiento de la memoria
            ultima_fila, ultima_col, ultimo_num = self.historial_movimientos.pop()
            
            # Si el número probado era menor a 9, intentaremos el siguiente número en esa celda
            if ultimo_num < 9:
                self.siguiente_numero_a_probar = ultimo_num + 1
                self.celda_actual_retroceso = (ultima_fila, ultima_col)
                self.modo_retroceso = False 
            else:
                # Si era 9, esa celda también se agotó; la borramos y seguimos retrocediendo
                self.siguiente_numero_a_probar = 1
                self.celda_actual_retroceso = None
                self.modo_retroceso = True
            
            # Le pedimos al entorno que borre el borrador equivocado (nunca una confirmada)
            action["name"] = "borrar"
            action["params"] = {"fila": ultima_fila, "columna": ultima_col}
            return action

        # PASO 2: Buscar en qué celda vamos a trabajar
        fila_objetivo, col_objetivo = -1, -1
        
        if self.celda_actual_retroceso:
            # Si venimos de borrar, retomamos esa celda donde la dejamos
            fila_objetivo, col_objetivo = self.celda_actual_retroceso
            inicio_rango = self.siguiente_numero_a_probar
            self.celda_actual_retroceso = None
        else:
            # Si no, buscamos la próxima celda vacía (0) en el tablero
            inicio_rango = 1
            for f in range(9):
                for c in range(9):
                    if tablero[f][c] == 0:
                        fila_objetivo, col_objetivo = f, c
                        break
                if fila_objetivo != -1:
                    break

<<<<<<< HEAD
        # PASO 3: Si recorrimos todo el tablero y no hay ceros, confirmamos los borradores pendientes
=======
        # Si recorrimos todo el tablero y no hay ceros, ganamos
>>>>>>> a5055bf3eb912404a50b98a1911991469fb66682
        if fila_objetivo == -1:
            borradores = estado_celda.get("borradores", [])
            if borradores:
                # Tomamos el primer borrador y procedemos a confirmarlo formalmente
                f_conf, c_conf = borradores[0]
                val_conf = tablero[f_conf][c_conf]
                action["name"] = "confirmar"
                action["params"] = {"fila": f_conf, "columna": c_conf, "valor": val_conf}
                return action
            else:
                print("\n¡El Agente ha resuelto y confirmado el Sudoku exitosamente!")
                action["name"] = "esperar" # Acción neutra
                return action

        # PASO 4: Pensar y actuar (Probar números válidos en borrador)
        for numero in range(inicio_rango, 10):
            if self._es_valido(tablero, fila_objetivo, col_objetivo, numero):
                # Anotamos en memoria que vamos a probar este número
                self.historial_movimientos.append((fila_objetivo, col_objetivo, numero))
                
                # Escribimos exclusivamente en borrador (sin confirmar prematuramente)
                action["name"] = "escribir"
                action["params"] = {"fila": fila_objetivo, "columna": col_objetivo, "valor": numero}
                return action

        # PASO 5: Si probamos del 1 al 9 y ninguno sirvió, entramos en modo retroceso
        self.modo_retroceso = True
        return self.function(percept)

    def __init__(self, env: SimulatedEnvironment):
        super().__init__()
        env.add(self.id)

        # --- Variables de memoria para el Backtracking y la búsqueda de soluciones ---
        
        self.historial_movimientos = [] # Guardará tuplas: (fila, columna, numero_probado)
        self.modo_retroceso = False     # Bandera para saber si estamos deshaciendo un camino sin salida
        self.celda_actual_retroceso = None
        self.siguiente_numero_a_probar = 1

        # --- Sensores y actuadores ---
        tablero_sensor = TableroSensor(env)
        tablero_sensor.agent = self
        self.add_sensor("tablero_sensor", tablero_sensor)

        vidas_sensor = VidasSensor(env)
        vidas_sensor.agent = self
        self.add_sensor("vidas_sensor", vidas_sensor)

        penalizacion_sensor = PenalizacionSensor(env)
        penalizacion_sensor.agent = self
        self.add_sensor("penalizacion_sensor", penalizacion_sensor)

        tiempo_total_sensor = Tiempo_totalSensor(env)
        tiempo_total_sensor.agent = self
        self.add_sensor("tiempo_total_sensor", tiempo_total_sensor)

        estado_celda_sensor = EstadoCeldaSensor(env)
        estado_celda_sensor.agent = self
        self.add_sensor("estado_celda_sensor", estado_celda_sensor)

        escribir_actuator = EscribirActuator(env)
        escribir_actuator.agent = self
        self.add_actuator("escribir_actuator", escribir_actuator)

        borrar_actuator = BorrarActuator(env)
        borrar_actuator.agent = self
        self.add_actuator("borrar_actuator", borrar_actuator)

        confirmar_actuator = ConfirmarActuator(env)
        confirmar_actuator.agent = self
        self.add_actuator("confirmar_actuator", confirmar_actuator)

    def print_state(self):
        tablero = self._sensors["tablero_sensor"].sense()
        estado_celda = self._sensors["estado_celda_sensor"].sense()
        vidas = self._sensors["vidas_sensor"].sense()
        penalizacion = self._sensors["penalizacion_sensor"].sense()
        tiempo_total = self._sensors["tiempo_total_sensor"].sense()

        print("+-------+-------+-------+")
        for r in range(9):
            fila_str = "| "
            for c in range(9):
                val = tablero[r][c]
                char = str(val) if val != 0 else "."
                fila_str += char + " "
                if (c + 1) % 3 == 0:
                    fila_str += "| "
            print(fila_str)
            if (r + 1) % 3 == 0:
                print("+-------+-------+-------+")

        num_confirmadas = len(estado_celda.get("confirmadas", []))
        num_borradores = len(estado_celda.get("borradores", []))
        num_pistas = len(estado_celda.get("pistas", []))

        print(f"Vidas restantes: {vidas} | Penalización acumulada: {penalizacion}s | Tiempo total: {tiempo_total:.4f}s")
        print(f"Pistas iniciales: {num_pistas} | Confirmadas: {num_confirmadas} | Borradores activos: {num_borradores}")

    def _perceive(self):
        percept = {}
        for sensor in self._sensors:
            percept[sensor] = self._sensors[sensor].sense()
        return percept
    
    def _act(self, percept):
        action = self.function(percept)

        action_actuators = {
            "escribir": (self._actuators["escribir_actuator"], ["fila", "columna", "valor"]),
            "borrar": (self._actuators["borrar_actuator"], ["fila", "columna"]),
            "confirmar": (self._actuators["confirmar_actuator"], ["fila", "columna", "valor"]) # Agregar parámetros
        }

        actuator, expected_params = action_actuators.get(action["name"], (None, None))
        if actuator:
            args = [action["params"].get(param) for param in expected_params]
            actuator.act(*args)
        
    def behave(self):
        percept = self._perceive()
        self._act(percept)


if __name__ == "__main__":
    from sudokuworld import EntornoSudoku
    print("--- SIMULACIÓN DE PRUEBA: SUDOKU AGENT ---")
    env = EntornoSudoku()
    agent = SudokuAgent(env)

    print("\nEstado inicial del tablero:")
    agent.print_state()

    print("\nEjecutando pasos del agente...")
    for i in range(100):
        agent.behave()
        if i % 20 == 0:
            print(f"\n--- Paso {i} ---")
            agent.print_state()

    print("\n--- Estado Final tras 100 pasos ---")
    agent.print_state()


