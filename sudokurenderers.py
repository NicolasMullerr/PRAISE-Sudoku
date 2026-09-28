from renderers import IRenderer
    
    # Funciones de ayuda (Helpers) que pueden ir fuera de la clase
def tablero_a_string(tablero):
        return "".join(str(tablero[f][c]) for f in range(9) for c in range(9))
    
def formatear_sudoku(tablero_str):
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
    
  
# La Clase Principal
class ConsoleRenderer(IRenderer):
    def __init__(self):          
        self.environment_statebuffer = None
    
    def observe(self, statebuffer):
        # Solo guardamos la referencia al buffer, no dibujamos todavía
        self.environment_statebuffer = statebuffer
    
    def render(self):
        # 1. Pedimos el estado actual
        state = self.environment_statebuffer.get_state()
            
        # 2. Si hay un estado nuevo, lo dibujamos
        if state:
            tablero = state.get("tablero")
            vidas = state.get("vidas")    
            penalizacion = state.get("penalizacion")
            # Extraemos la data para dibujar        
                
            # Usamos tus funciones de ayuda para armar el tablero visual
            tablero_str = tablero_a_string(tablero)
            cuadricula = formatear_sudoku(tablero_str)
            print(cuadricula)
            tiempo_total = state.get("tiempo_total", 0.0)
            estado_celda = state.get("estado_celda", {})
            num_confirmadas = len(estado_celda.get("confirmadas", []))
            num_borradores = len(estado_celda.get("borradores", []))
            num_pistas = len(estado_celda.get("pistas", []))
            print(f"Vidas restantes: {vidas} | Penalización acumulada: {penalizacion}s | Tiempo total: {tiempo_total:.4f}s")
            print(f"Pistas iniciales: {num_pistas} | Confirmadas: {num_confirmadas} | Borradores activos: {num_borradores}")
