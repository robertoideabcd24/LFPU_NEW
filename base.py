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
    
class Booleano:
    def __init__(self, valor):
        self.valor = valor
    
    def __repr__(self):
        return f"Booleano({self.valor})"
    
class OperacionUnaria:
    def __init__(self, operador, expresion):
        self.operador = operador
        self.expresion = expresion

    def __repr__(self):
        return f"OperacionUnaria({self.operador} {self.expresion})"
    
class If:
    def __init__(self, condicion, cuerpo, elifs=None, else_cuerpo=None):
        self.condicion = condicion
        self.cuerpo = cuerpo
        self.elifs = elifs if elifs is not None else []
        self.else_cuerpo = else_cuerpo

    def __repr__(self):
        parts = [f"If({self.condicion}): {self.cuerpo}"]
        for cond, cuerpo in self.elifs:
            parts.append(f"Elif({cond}): {cuerpo}")
        if self.else_cuerpo:
            parts.append(f"Else: {self.else_cuerpo}")
        return "\n".join(parts)

class Bloque:
    def __init__(self, declaraciones):
        self.declaraciones = declaraciones
    
    def __repr__(self):
        return f"Bloque({self.declaraciones})"