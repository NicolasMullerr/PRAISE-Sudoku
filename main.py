import time
from sudokuworld import EntornoSudoku
from sudokuagent import SudokuAgent

def main():
    print("==================================================")
    print("     INICIANDO PRAISE-Sudoku - SIMULACIÓN         ")
    print("==================================================")

    # 1. Instanciamos el entorno y el agente de Sudoku
    env = EntornoSudoku()
    agent = SudokuAgent(env)

    print(f"\nID del Agente: {agent.id}")
    print("\n--- ESTADO INICIAL DEL TABLERO ---")
    agent.print_state()

    print("\n--- EJECUTANDO ACCIONES DEL AGENTE ---")
    pasos = 1_500_000  # Margen holgado; el agente suele resolver en ~1.04M pasos
    for i in range(1, pasos + 1):
        agent.behave()

        # Cortamos en cuanto no quede ninguna celda vacía Y no haya borradores pendientes.
        tablero = agent._sensors["tablero_sensor"].sense()
        estado  = agent._sensors["estado_celda_sensor"].sense()
        if (all(tablero[f][c] != 0 for f in range(9) for c in range(9))
                and len(estado.get("borradores", [])) == 0):
            print(f"\n¡El Agente ha resuelto el Sudoku en {i} pasos!")
            break

        if i % 1 == 0 or i == 1:
            print(f"\n[Paso {i}/{pasos}]")
            agent.print_state()


    print("\n==================================================")
    print("--- ESTADO FINAL TRAS LA SIMULACIÓN ---")
    agent.print_state()
    print("==================================================")

if __name__ == '__main__':
    main()