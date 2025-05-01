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
        # para que acepte una expresión completa
        self.expresion = expresion  
    
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
    
class Clase:
    def __init__(self, nombre, atributos=None, metodos=None):
        self.nombre = nombre
        self.atributos = atributos or []
        self.metodos = metodos or []

    def __repr__(self):
        return f"Clase({self.nombre}, atributos: {self.atributos})"

class InstanciaClase:
    def __init__(self, clase):
        self.clase = clase
        self.atributos = {nombre: None for nombre in clase.atributos}
        # Inicializar atributos declarados en la clase
        for atributo in clase.atributos:
            self.atributos[atributo] = None
    
    def __repr__(self):
        atribs = ', '.join(f"{k}={v}" for k, v in self.atributos.items())
        return f"Instancia de {self.clase.nombre} con atributos {self.atributos}"
    
    def __getattr__(self, name):
        if name in self.atributos:
            if self.atributos[name] is None:
                raise AttributeError(f"Atributo '{name}' no ha sido asignado")
            return self.atributos[name]
        raise AttributeError(f"La clase '{self.clase.nombre}' no tiene atributo '{name}'")
    
    def __setattr__(self, name, value):
        if name in ['clase', 'atributos']:
            super().__setattr__(name, value)
        elif name in getattr(self, 'atributos', {}):
            self.atributos[name] = value
        else:
            raise AttributeError(f"La clase '{self.clase.nombre}' no tiene atributo '{name}'")
    
class CreacionInstancia:
    def __init__(self, nombre_instancia, nombre_clase):
        self.nombre_instancia = nombre_instancia
        self.nombre_clase = nombre_clase
    
    def __repr__(self):
        return f"CreacionInstancia({self.nombre_instancia} := {self.nombre_clase}())"

class ExitCommand:
    def __repr__(self):
        return "ExitCommand()"

class Atributo:
    def __init__(self, nombre):
        self.nombre = nombre

    def __repr__(self):
        return f"Atributo(nombre='{self.nombre}')"

class AsignacionAtributo:
    def __init__(self, nombre_instancia, nombre_atributo, valor):
        self.nombre_instancia = nombre_instancia
        self.nombre_atributo = nombre_atributo
        self.valor = valor
    
    def __repr__(self):
        return f"AsignacionAtributo({self.objeto}.{self.atributo} = {self.valor})"