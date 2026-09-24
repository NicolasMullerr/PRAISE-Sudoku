import time
import os
import sys
from sudokuworld import EntornoSudoku
from sudokuagent import SudokuAgent

ARCHIVO_RESUELTOS = "sudokus_resueltos.txt"
ARCHIVO_NO_RESUELTOS = "sudokus_no_resueltos.txt"
MAX_PASOS_DEFAULT = 20000
SALTOS_DEFAULT = 10000

def tablero_a_string(tablero): # Convierte un tablero de Sudoku (lista de listas) en un string de 81 caracteres.  
    return "".join(str(tablero[f][c]) for f in range(9) for c in range(9))

def formatear_sudoku(tablero_str): # Convierte un string de 81 caracteres en un string formateado de 9x9 visual.    
    res = []
    res.append("+-------+-------+-------+")
    for r in range(9):
        row = ""
        for c in range(9):
            if c % 3 == 0:
                row += "| "
            val = tablero_str[r*9 + c]
            row += (val if val != '0' else '.') + " "
        row += "|"
        res.append(row)
        if (r + 1) % 3 == 0:
            res.append("+-------+-------+-------+")
    return "\n".join(res)

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
        
        f.write("Resultado del Agente:\n")
        f.write(formatear_sudoku(tablero_agente_str) + "\n\n")
        
        f.write("Sudoku Resuelto:\n")
        f.write(formatear_sudoku(tablero_resuelto_str) + "\n")
        f.write("==================================================\n\n")

def ejecutar_partida(tablero_inicial=None, max_pasos=MAX_PASOS_DEFAULT, saltos=SALTOS_DEFAULT):
    #    Ejecuta una simulación completa de un agente resolviendo un Sudoku. Determina si fue resuelto en max_pasos o menos.
    env = EntornoSudoku(tablero_inicial=tablero_inicial)
    agent = SudokuAgent(env)
    
    # Obtenemos la representación del tablero inicial (las pistas antes de empezar a jugar)
    tablero_inicial_str = tablero_a_string(env.tablero)
    
    # Resolver para obtener el tablero resuelto
    env_solved = EntornoSudoku(tablero_inicial=tablero_inicial_str)
    env_solved._resolver_tablero_backtracking()
    tablero_resuelto_str = tablero_a_string(env_solved.tablero)
    
    resuelto = False
    pasos_ejecutados = 0
    
    for paso in range(1, max_pasos + 1):
        agent.behave()
        pasos_ejecutados = paso
        
        tablero_actual = agent._sensors["tablero_sensor"].sense()
        estado = agent._sensors["estado_celda_sensor"].sense()
        # El Sudoku está resuelto cuando no quedan ceros en el tablero y no hay borradores pendientes
        if not any(0 in fila for fila in tablero_actual) and len(estado.get("borradores", [])) == 0:
            resuelto = True
            break
            
        # Si el agente se queda sin vidas, finaliza la partida
        vidas = agent._sensors["vidas_sensor"].sense()
        if vidas <= 0:
            break
            
        if saltos > 0 and (paso % saltos == 0 or paso == 1):
            print(f"\n[Paso {paso}/{max_pasos}]")
            agent.print_state()
            
    # Mostrar el estado final si no se mostró en el último paso
    if saltos > 0 and pasos_ejecutados % saltos != 0:
        print(f"\n[Paso Final {pasos_ejecutados}/{max_pasos}]")
        agent.print_state()
        
    tablero_agente_str = tablero_a_string(agent._sensors["tablero_sensor"].sense())
        
    return resuelto, pasos_ejecutados, tablero_inicial_str, tablero_agente_str, tablero_resuelto_str, agent

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
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
