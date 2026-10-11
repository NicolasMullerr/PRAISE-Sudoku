import time
import os
import sys
import threading
from sudokuworld import EntornoSudoku
from sudokuagent import SudokuAgent
from sudokurenderers import ConsoleRenderer, tablero_a_string, formatear_sudoku
from statebuffer import StateBuffer

ARCHIVO_RESUELTOS = "sudokus_resueltos.txt"
ARCHIVO_NO_RESUELTOS = "sudokus_no_resueltos.txt"
MAX_PASOS_DEFAULT = 20000
SALTOS_DEFAULT = 10000

def guardar_resultado(tablero_inicial_str, tablero_agente_str, tablero_resuelto_str, resuelto, pasos, archivo_resueltos=ARCHIVO_RESUELTOS, archivo_no_resueltos=ARCHIVO_NO_RESUELTOS):
    # Registra los resultados en el archivo de texto correspondiente. 
    archivo_destino = archivo_resueltos if resuelto else archivo_no_resueltos
    modo = "a" if os.path.exists(archivo_destino) else "w"
    
    with open(archivo_destino, modo, encoding="utf-8") as f:
        f.write("==================================================\n")
        estado_str = "Resuelto" if resuelto else f"No resuelto (límite de {pasos} pasos alcanzado)"
        f.write(f"Resultado: {estado_str} | Pasos: {pasos}\n\n")
        
        f.write("Sudoku Inicial:\n")
        f.write(formatear_sudoku(tablero_inicial_str) + "\n\n")
        f.write(tablero_inicial_str + "\n\n")

        f.write("Resultado del Agente:\n")
        f.write(formatear_sudoku(tablero_agente_str) + "\n\n")
        
        f.write("Sudoku Resuelto:\n")
        f.write(formatear_sudoku(tablero_resuelto_str) + "\n")
        f.write("==================================================\n\n")

def ejecutar_partida(tablero_inicial=None, max_pasos=MAX_PASOS_DEFAULT, saltos=SALTOS_DEFAULT, agent_delay=0.0):
    # Ejecuta una simulación de un agente resolviendo un Sudoku en un hilo concurrente.
    env = EntornoSudoku(tablero_inicial=tablero_inicial)
    agent = SudokuAgent(env)
    renderer = ConsoleRenderer()
    buffer = StateBuffer(agent.id, env)
    renderer.observe(buffer)
    
    # Obtenemos la representación del tablero inicial (las pistas antes de empezar a jugar)
    tablero_inicial_str = tablero_a_string(env.tablero)
    
    # Resolver para obtener el tablero resuelto
    env_solved = EntornoSudoku(tablero_inicial=tablero_inicial_str)
    env_solved._resolver_tablero_backtracking()
    tablero_resuelto_str = tablero_a_string(env_solved.tablero)
    
    if saltos > 0:
        print("\n[Tablero Inicial]")
        renderer.render()
    
    pasos_contador = [0]
    lock_render = threading.Lock()

    def agent_worker():
        while not agent.is_stopped() and pasos_contador[0] < max_pasos:
            agent.behave()
            pasos_contador[0] += 1

            tablero_actual = agent._sensors["tablero_sensor"].sense()
            estado = agent._sensors["estado_celda_sensor"].sense()
            if not any(0 in fila for fila in tablero_actual) and len(estado.get("borradores", [])) == 0:
                agent.stop()
                break

            vidas = agent._sensors["vidas_sensor"].sense()
            if vidas <= 0:
                agent.stop()
                break

            if saltos > 0 and (pasos_contador[0] % saltos == 0 or pasos_contador[0] == 1):
                with lock_render:
                    print(f"\n[Paso {pasos_contador[0]}/{max_pasos}]")
                    renderer.render()

            if agent_delay > 0:
                time.sleep(agent_delay)
        agent.stop()

    agent_thread = threading.Thread(target=agent_worker, name="AgentThread", daemon=True)
    agent_thread.start()
    agent_thread.join()

    pasos_ejecutados = pasos_contador[0]
    tablero_final = agent._sensors["tablero_sensor"].sense()
    estado_final = agent._sensors["estado_celda_sensor"].sense()
    resuelto = not any(0 in fila for fila in tablero_final) and len(estado_final.get("borradores", [])) == 0

    # Mostrar el estado final si no se mostró en el último paso
    if saltos > 0 and pasos_ejecutados % saltos != 0:
        print(f"\n[Paso Final {pasos_ejecutados}/{max_pasos}]")
        renderer.render()
        
    tablero_agente_str = tablero_a_string(tablero_final)
        
    return resuelto, pasos_ejecutados, tablero_inicial_str, tablero_agente_str, tablero_resuelto_str, agent

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        # Hay que ingresar los tableros como strings de 81 caracteres
        print("Uso:")
        print("  python main.py                         # Ejecuta 1 partida con parámetros por defecto")
        print("  python main.py <max_pasos>             # Ejecuta 1 partida especificando máximo de pasos")
        print("  python main.py <max_pasos> <saltos>    # Especifica máximo de pasos y cada cuántos se muestra el tablero")
        print("  python main.py --cargar <fuente>       # Prueba un tablero específico (string o ruta .txt)")
        print("  python main.py --interactivo           # Permite ingresar el tablero de Sudoku a mano en la consola")
        return

    fuente = None
    max_pasos = MAX_PASOS_DEFAULT
    saltos = SALTOS_DEFAULT

    if len(sys.argv) > 1 and sys.argv[1] == "--interactivo":
        fuente = "interactivo"
        if len(sys.argv) > 2 and sys.argv[2].isdigit():
            max_pasos = int(sys.argv[2])
        if len(sys.argv) > 3 and sys.argv[3].isdigit():
            saltos = int(sys.argv[3])
    elif len(sys.argv) > 1 and sys.argv[1] == "--cargar":
        if len(sys.argv) > 2:
            fuente = sys.argv[2]
            print(f"Cargando tablero desde: {fuente}")
            if len(sys.argv) > 3 and sys.argv[3].isdigit():
                max_pasos = int(sys.argv[3])
            if len(sys.argv) > 4 and sys.argv[4].isdigit():
                saltos = int(sys.argv[4])
    else:
        if len(sys.argv) > 1 and sys.argv[1].isdigit():
            max_pasos = int(sys.argv[1])
        if len(sys.argv) > 2 and sys.argv[2].isdigit():
            saltos = int(sys.argv[2])

    print("==================================================")
    print(" INICIANDO EJECUCIÓN DE SUDOKU")
    print(f" Límite por partida: {max_pasos} pasos")
    print(f" Mostrar cada: {saltos} pasos")
    print("==================================================")

    t0 = time.time()
    resuelto, pasos, tab_ini_str, tab_ag_str, tab_res_str, agent = ejecutar_partida(tablero_inicial=fuente, max_pasos=max_pasos, saltos=saltos)
    duracion = time.time() - t0

    guardar_resultado(tab_ini_str, tab_ag_str, tab_res_str, resuelto, pasos)

    print("\n==================================================")
    print("               RESUMEN DE RESULTADOS              ")
    print("==================================================")
    if resuelto:
        print(f"[RESUELTO] en {pasos} pasos ({duracion:.2f}s) -> Guardado en {ARCHIVO_RESUELTOS}")
    else:
        print(f"[NO RESUELTO] tras {pasos} pasos ({duracion:.2f}s) -> Guardado en {ARCHIVO_NO_RESUELTOS}")
    print("==================================================")

if __name__ == '__main__':
    main()
