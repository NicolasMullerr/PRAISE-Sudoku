import time
import os
import sys
from sudokuworld import EntornoSudoku
from sudokuagent import SudokuAgent

ARCHIVO_RESUELTOS = "sudokus_resueltos_1000.txt"
ARCHIVO_NO_RESUELTOS = "sudokus_no_resueltos_1000.txt"
MAX_PASOS_DEFAULT = 1000


def tablero_a_string(tablero):
    """Convierte una matriz 9x9 en un string plano de 81 caracteres."""
    return "".join(str(tablero[f][c]) for f in range(9) for c in range(9))

def formatear_sudoku(tablero_str):
    """Convierte un string de 81 caracteres en un string formateado de 9x9 visual."""
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
    """Registra los resultados en el archivo de texto correspondiente."""
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

def ejecutar_partida(tablero_inicial=None, max_pasos=1000, mostrar_progreso=False):
    """
    Ejecuta una simulación completa de un agente resolviendo un Sudoku.
    Determina si fue resuelto en max_pasos o menos.
    """
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
            
    return resuelto, pasos_ejecutados, tablero_inicial_str, agent


def clasificar_lote_sudokus(n_partidas=10, max_pasos=1000):
    """
    Ejecuta un lote de partidas con tableros aleatorios y los clasifica
    en los dos archivos de texto según si se resuelven en max_pasos o menos.
    """
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
