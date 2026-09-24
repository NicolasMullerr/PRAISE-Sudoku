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


def guardar_resultado(tablero_str, resuelto, pasos, archivo_resueltos=ARCHIVO_RESUELTOS, archivo_no_resueltos=ARCHIVO_NO_RESUELTOS):
    """Registra el tablero inicial en el archivo de texto correspondiente."""
    archivo_destino = archivo_resueltos if resuelto else archivo_no_resueltos
    modo = "a" if os.path.exists(archivo_destino) else "w"
    
    with open(archivo_destino, modo, encoding="utf-8") as f:
        if resuelto:
            f.write(f"{tablero_str} | Pasos: {pasos}\n")
        else:
            f.write(f"{tablero_str} | No resuelto (límite de {pasos} pasos alcanzado)\n")


def ejecutar_partida(tablero_inicial=None, max_pasos=1000, mostrar_progreso=False):
    """
    Ejecuta una simulación completa de un agente resolviendo un Sudoku.
    Determina si fue resuelto en max_pasos o menos.
    """
    env = EntornoSudoku(tablero_inicial=tablero_inicial)
    agent = SudokuAgent(env)
    
    # Obtenemos la representación del tablero inicial (las pistas antes de empezar a jugar)
    tablero_inicial_str = tablero_a_string(env.tablero)
    
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
            
        if mostrar_progreso and (paso % 100 == 0 or paso == 1):
            print(f"[Paso {paso}/{max_pasos}]")
            agent.print_state()
            
    return resuelto, pasos_ejecutados, tablero_inicial_str, agent


def clasificar_lote_sudokus(n_partidas=10, max_pasos=1000):
    """
    Ejecuta un lote de partidas con tableros aleatorios y los clasifica
    en los dos archivos de texto según si se resuelven en max_pasos o menos.
    """
    print("==================================================")
    print(f" INICIANDO CLASIFICACIÓN DE SUDOKUS ({n_partidas} PARTIDAS)")
    print(f" Límite por partida: {max_pasos} pasos")
    print(f" Resueltos   -> {ARCHIVO_RESUELTOS}")
    print(f" No resueltos -> {ARCHIVO_NO_RESUELTOS}")
    print("==================================================")
    
    resueltos_count = 0
    no_resueltos_count = 0
    inicio_total = time.time()
    
    for i in range(1, n_partidas + 1):
        print(f"\n--- Ejecutando Partida {i}/{n_partidas} ---")
        t0 = time.time()
        resuelto, pasos, tablero_str, _ = ejecutar_partida(max_pasos=max_pasos, mostrar_progreso=False)
        duracion = time.time() - t0
        
        guardar_resultado(tablero_str, resuelto, pasos)
        
        if resuelto:
            resueltos_count += 1
            print(f"[RESUELTO] en {pasos} pasos ({duracion:.2f}s) -> Guardado en {ARCHIVO_RESUELTOS}")
        else:
            no_resueltos_count += 1
            print(f"[NO RESUELTO] tras {pasos} pasos ({duracion:.2f}s) -> Guardado en {ARCHIVO_NO_RESUELTOS}")
            
    tiempo_total = time.time() - inicio_total
    print("\n==================================================")
    print("               RESUMEN DE RESULTADOS              ")
    print("==================================================")
    print(f"Total partidas evaluadas: {n_partidas}")
    print(f"Resueltos (<= {max_pasos} pasos): {resueltos_count} ({resueltos_count / n_partidas * 100:.1f}%)")
    print(f"No resueltos (> {max_pasos} pasos): {no_resueltos_count} ({no_resueltos_count / n_partidas * 100:.1f}%)")
    print(f"Tiempo total de cómputo: {tiempo_total:.2f}s")
    print("==================================================")


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print("Uso:")
        print("  python main.py                         # Ejecuta lote por defecto (5 partidas, máx 1000 pasos)")
        print("  python main.py <n_partidas>            # Ejecuta n partidas aleatorias")
        print("  python main.py <n_partidas> <max_pas>  # Especifica n partidas y límite de pasos")
        print("  python main.py --cargar <fuente>       # Prueba un tablero específico (string o ruta .txt)")
        return

    if len(sys.argv) > 2 and sys.argv[1] == "--cargar":
        fuente = sys.argv[2]
        print(f"Cargando tablero desde: {fuente}")
        resuelto, pasos, tablero_str, agent = ejecutar_partida(tablero_inicial=fuente, max_pasos=MAX_PASOS_DEFAULT, mostrar_progreso=True)
        guardar_resultado(tablero_str, resuelto, pasos)
        print(f"\nResultado: {'RESUELTO' if resuelto else 'NO RESUELTO'} en {pasos} pasos.")
        agent.print_state()
        return

    n_partidas = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 5
    max_pasos = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else MAX_PASOS_DEFAULT

    clasificar_lote_sudokus(n_partidas=n_partidas, max_pasos=max_pasos)


if __name__ == '__main__':
    main()