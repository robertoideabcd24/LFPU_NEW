# base.py
class Numero:
    def __init__(self, valor):
        self.valor = valor
    
    def __repr__(self):
        return f"Numero({self.valor})"
    
class Variable:
    def __init__(self, nombre):
        self.nombre = nombre
    
    def __repr__(self):
        return f"Variable({self.nombre})"

class OperacionBinaria:
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha

    def __repr__(self):
        return f"OperacionBinaria({self.izquierda} {self.operador} {self.derecha})"

class Asignacion:
    def __init__(self, nombre_var, valor):
        self.nombre_var = nombre_var
        self.valor = valor

    def __repr__(self):
        return f"Asignacion({self.nombre_var} = {self.valor})"
    
class Prt:
    def __init__(self, expresion):
        self.expresion = expresion  # Ahora acepta una expresión completa
    
    def __repr__(self):
        return f"Prt({self.expresion})"
    
class Cadena:
    def __init__(self, valor):
        self.valor = valor
    
    def __repr__(self):
        return f"Cadena('{self.valor}')"