class Colors:
    # Colores principales (los que quiero mantener)
    VARIABLE = '\033[94m'      # Azul (se mantiene)
    NUMERO = '\033[92m'        # Verde (se mantiene)
    OPERADOR = '\033[93m'      # Amarillo (se mantiene)
    
    # Colores para cambiar:
    ASIGNACION = '\033[95m'    # Magenta (nuevo color para asignaciones)
    CYAN = '\033[96m'          # Cian (solo para títulos)
    FAIL = '\033[91m'          # Rojo (para errores, se mantiene)
    RESET = '\033[0m'          # Reset
    
    # Más variedad
    TITULO = '\033[1;36m'      # Cyan negrita para títulos
    EXITO = '\033[1;32m'       # Verde negrita para mensajes positivos

    PRINT = '\033[38;5;213m'  # Color morado claro para Prt