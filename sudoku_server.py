from statebuffer import IStateBuffer, StateBuffer
from sudokuworld import EntornoSudoku
import Pyro4


class EntornoSudokuPyroAdapter:
    def __init__(self, daemon, ns):
        self._sudokuenv = None
        self._daemon = daemon
        self._ns = ns
        self._buffers = {}

    @Pyro4.expose
    def build_env(self, tablero_inicial=None):
        """Construye el EntornoSudoku.
        tablero_inicial puede ser:
          - None              → genera tablero aleatorio
          - string de 81 dígitos → carga ese tablero
          - ruta a .txt       → carga desde archivo
        """
        self._sudokuenv = EntornoSudoku(tablero_inicial=tablero_inicial)

    @Pyro4.expose
    def create_statebuffer(self, agent_id: int) -> str:
        if self._sudokuenv is None:
            raise RuntimeError("Entorno no construido. Llamar build_env() primero.")

        buffer = StateBuffer(agent_id, self._sudokuenv)
        buffer_adapter = StateBufferPyroAdapter(buffer)

        uri = self._daemon.register(buffer_adapter)
        name = f"statebuffer.agent_{agent_id}"
        self._ns.register(name, uri)

        self._sudokuenv.add_statebuffer(agent_id, buffer)
        self._buffers[agent_id] = buffer

        return name

    @Pyro4.expose
    def add(self, agent_id: int) -> None:
        if self._sudokuenv is not None:
            self._sudokuenv.add(agent_id)

    @Pyro4.expose
    def remove(self, agent_id: int) -> None:
        if self._sudokuenv is not None:
            self._sudokuenv.remove(agent_id)

    @Pyro4.expose
    def add_statebuffer(self, agent_id: int, statebuffer: IStateBuffer) -> None:
        if self._sudokuenv is not None:
            self._sudokuenv.add_statebuffer(agent_id, statebuffer)

    @Pyro4.expose
    def remove_statebuffer(self, agent_id: int, statebuffer_id: int) -> None:
        if self._sudokuenv is not None:
            self._sudokuenv.remove(agent_id, statebuffer_id)

    @Pyro4.expose
    def get_property(self, agent_id: int, property_name: str) -> dict:
        response = {}
        if self._sudokuenv is not None:
            response = self._sudokuenv.get_property(agent_id, property_name)
        return response

    @Pyro4.expose
    def take_action(self, agent_id: int, action_name: str, params: dict = {}) -> None:
        if self._sudokuenv is not None:
            self._sudokuenv.take_action(agent_id, action_name, params)


@Pyro4.expose
class StateBufferPyroAdapter:
    def __init__(self, buffer: StateBuffer):
        self._buffer = buffer

    def update(self, state):
        return self._buffer.update(state)

    def get_state(self):
        return self._buffer.get_state()


if __name__ == '__main__':
    daemon = Pyro4.Daemon(host="localhost")
    ns = Pyro4.locateNS()
    env_adapter = EntornoSudokuPyroAdapter(daemon, ns)
    env_uri = daemon.register(env_adapter)
    ns.register("sudokuworld", env_uri)
    print(f"[Servidor Sudoku] Registrado en nameserver como 'sudokuworld'")
    print(f"[Servidor Sudoku] URI: {env_uri}")
    print(f"[Servidor Sudoku] Esperando conexiones...")
    daemon.requestLoop()
