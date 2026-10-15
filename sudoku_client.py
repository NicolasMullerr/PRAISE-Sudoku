import threading
import Pyro4
from sudokuagent import SudokuAgent
from sudokurenderers import ConsoleRenderer

MAX_PASOS = 20000

event_sync_start = threading.Event()
event_render_ready = threading.Event()


def agent_thread(agent):
    """Hilo del agente: espera a que el renderer esté listo y ejecuta behave() en loop."""
    event_sync_start.wait(timeout=5)  # Espera a que el renderer esté listo
    pasos = 0
    while not agent.is_stopped() and pasos < MAX_PASOS:
        event_render_ready.wait(timeout=0.1)  # Sincronización con renderer
        agent.behave()
        event_render_ready.clear()
        pasos += 1
    agent.stop()  # Seguro aunque ya esté detenido


def render_thread(renderer, agent):
    """Hilo del renderer: dibuja el estado y señaliza al agente que puede actuar."""
    while not agent.is_stopped():
        renderer.render()
        event_sync_start.set()    # Señal: renderer listo, agente puede arrancar
        event_render_ready.set()  # Señal: renderer terminó, agente puede actuar


# --- Setup ---
sudokuenv = Pyro4.Proxy("PYRONAME:sudokuworld")
sudokuenv.build_env(tablero_inicial=None)   # None = genera tablero aleatorio

agent = SudokuAgent(sudokuenv)

statebuffer_name = sudokuenv.create_statebuffer(agent.id)
statebuffer = Pyro4.Proxy(f"PYRONAME:{statebuffer_name}")

renderer = ConsoleRenderer()
renderer.observe(statebuffer)
print(f"[Cliente Sudoku] Agente ID: {agent.id}")
print(f"[Cliente Sudoku] Iniciando partida (max {MAX_PASOS} pasos)...")

# --- Hilos ---
thread_agent = threading.Thread(target=agent_thread, args=(agent,), name="AgentThread")
thread_renderer = threading.Thread(target=render_thread, args=(renderer, agent), name="RendererThread")

# El renderer arranca primero para estar listo antes de que el agente actúe
thread_renderer.start()
thread_agent.start()

thread_agent.join()
thread_renderer.join()

print("\n[Cliente Sudoku] Partida finalizada.")
