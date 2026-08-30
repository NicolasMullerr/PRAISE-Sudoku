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
        request_info = {"fila": fila, "columna": columna, "valor": valor}
        self._env.take_action(self._agent.id, "escribir", request_info)

class BorrarActuator(SimulatedActuator):

    def act(self, fila: int, columna: int):
        request_info = {"fila": fila, "columna": columna}
        self._env.take_action(self._agent.id, "borrar", request_info)

class ConfirmarActuator(SimulatedActuator):
    def act(self, fila: int, columna: int, valor: int):
        request_info = {"fila": fila, "columna": columna, "numero": valor} # Ojo: en el entorno usas "numero"
        self._env.take_action(self._agent.id, "confirmar", request_info)

# Ahora definimos el agente del juego de Sudoku

class SudokuAgent(Agent):

    def function(self, percept):
        # Aquí se implementaría la lógica del agente para decidir qué acción tomar
        action = {}
        # Ejemplo de acción: escribir un valor en una celda
        action["name"] = "escribir"
        action["params"] = {"fila": 0, "columna": 0, "valor": 1}
        return action

    def __init__(self, env: SimulatedEnvironment):
        super().__init__()
        env.add(self.id)

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
        print("Estado del tablero: {}".format(self._sensors["tablero_sensor"].sense()))
        print("Vidas restantes: {}".format(self._sensors["vidas_sensor"].sense()))
        print("Penalización actual: {}".format(self._sensors["penalizacion_sensor"].sense()))
        print("Tiempo total: {}".format(self._sensors["tiempo_total_sensor"].sense()))
        print("Estado de la celda actual: {}".format(self._sensors["estado_celda_sensor"].sense()))

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

