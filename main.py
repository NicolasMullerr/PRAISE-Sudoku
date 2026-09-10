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
    pasos = 50
    for i in range(1, pasos + 1):
        agent.behave()
        if i % 10 == 0 or i == 1:
            print(f"\n[Paso {i}/{pasos}]")
            agent.print_state()

    print("\n==================================================")
    print("--- ESTADO FINAL TRAS LA SIMULACIÓN ---")
    agent.print_state()
    print("==================================================")

if __name__ == '__main__':
    main()