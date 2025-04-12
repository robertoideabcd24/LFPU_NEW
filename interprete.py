from base import Numero, Variable, OperacionBinaria, Asignacion
from colors import Colors

class Interpreter:
    def __init__(self):
        self.memoria = {}

    def ejecutar(self, ast, debug=False):
        ultimo_resultado = None
        for declaracion in ast:
            if isinstance(declaracion, Asignacion):
                if debug:
                    print(f"\nProcesando asignación: {declaracion.nombre_var}")
                
                valor = self.evaluar_expresion(declaracion.valor, debug)
                self.memoria[declaracion.nombre_var] = valor
                
                if debug:
                    print(f"Asignación completada: {declaracion.nombre_var} = {valor}")
                
                ultimo_resultado = valor
        return ultimo_resultado

    def ejecutar_asignacion(self, asignacion):
        # Maneja tanto números directos como operaciones binarias
        if isinstance(asignacion.valor, (Numero, Variable)):
            valor = self.evaluar_expresion(asignacion.valor)
        elif isinstance(asignacion.valor, OperacionBinaria):
            valor = self.evaluar_operacion_binaria(asignacion.valor)
        else:
            raise ValueError(f"Tipo de expresión no soportada: {type(asignacion.valor)}")
        
        self.memoria[asignacion.nombre_var] = valor
        print(f"Asignación: {asignacion.nombre_var} = {valor}")

    def evaluar_operacion_binaria(self, operacion):
        izquierda = self.evaluar_expresion(operacion.izquierda)
        derecha = self.evaluar_expresion(operacion.derecha)

        # Conversión implícita de tipos
        if isinstance(izquierda, int) and isinstance(derecha, float):
            izquierda = float(izquierda)
        elif isinstance(derecha, int) and isinstance(izquierda, float):
            derecha = float(derecha)

        if operacion.operador == '+':
            return izquierda + derecha
        elif operacion.operador == '-':
            return izquierda - derecha
        elif operacion.operador == '*':
            return izquierda * derecha
        elif operacion.operador == '/':
            return izquierda / derecha  # División que puede resultar en float
        else:
            raise ValueError(f"Operador no soportado: '{operacion.operador}'")

    def evaluar_expresion(self, expr, debug=False):
        if debug:
            print(f"Evaluando expresión: {expr}")

        if isinstance(expr, Numero):
            return expr.valor
        elif isinstance(expr, Variable):
            if expr.nombre not in self.memoria:
                raise NameError(f"Variable no definida: '{expr.nombre}'")
            return self.memoria[expr.nombre]
        elif isinstance(expr, OperacionBinaria):
            izquierda = self.evaluar_expresion(expr.izquierda, debug)
            derecha = self.evaluar_expresion(expr.derecha, debug)
            if debug:
                print(f"Operación: {izquierda} {expr.operador} {derecha}")
            return self.evaluar_operacion_binaria(expr)
        else:
            raise ValueError(f"Tipo de expresión no soportada: {type(expr)}")

    def imprimir_memoria(self):
        """Muestra las variables con colores"""
        if not self.memoria:
            print("(no hay variables definidas)")
            return
            
        for var, valor in self.memoria.items():
            # Determinar el tipo de valor para el color
            if isinstance(valor, (int, float)):
                valor_str = f"{Colors.NUMERO}{valor}{Colors.RESET}"
            else:
                valor_str = str(valor)
                
            print(f"{Colors.VARIABLE}{var}{Colors.RESET}: {valor_str}")
