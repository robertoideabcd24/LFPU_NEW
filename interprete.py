from base import Numero, Variable, OperacionBinaria, Asignacion

class Interpreter:
    def __init__(self):
        self.memoria = {}

    def ejecutar(self, ast):
        ultimo_resultado = None
        for declaracion in ast:
            if isinstance(declaracion, Asignacion):
                # Primero evaluar y guardar en memoria
                if isinstance(declaracion.valor, (Numero, Variable, OperacionBinaria)):
                    valor = self.evaluar_expresion(declaracion.valor)
                    self.memoria[declaracion.nombre_var] = valor
                    print(f"Asignación: {declaracion.nombre_var} = {valor}")
                    ultimo_resultado = valor  # Luego actualizar último resultado
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

    def evaluar_expresion(self, expr):
        if isinstance(expr, Numero):
            return expr.valor
        elif isinstance(expr, Variable):
            if expr.nombre not in self.memoria:
                raise NameError(f"Variable no definida: '{expr.nombre}'")
            return self.memoria[expr.nombre]
        elif isinstance(expr, OperacionBinaria):
            return self.evaluar_operacion_binaria(expr)
        else:
            raise ValueError(f"Tipo de expresión no soportada: {type(expr)}")

    def imprimir_memoria(self):
        for var, valor in self.memoria.items():
            print(f"{var}: {valor}")
