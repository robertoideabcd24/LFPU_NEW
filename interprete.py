from base import Numero, Variable, OperacionBinaria, Asignacion, Prt, Cadena, OperacionUnaria, If, Bloque
from colors import Colors

class Interpreter:
    def __init__(self):
        self.memoria = {}
        self.silent_mode = False

    def ejecutar(self, ast, debug=False):
        ultimo_resultado = None
        for declaracion in ast:
            if isinstance(declaracion, Asignacion):
                valor = self.evaluar_expresion(declaracion.valor, debug)
                self.memoria[declaracion.nombre_var] = valor
                ultimo_resultado = valor
                if debug:
                    print(f"[DEBUG] Asignado: {declaracion.nombre_var} = {valor}")
            elif isinstance(declaracion, Prt):
                resultado = self.evaluar_expresion(declaracion.expresion, debug)
                print(resultado)  # Siempre mostrar Prt
            elif isinstance(declaracion, If):
                self.evaluar_if(declaracion, debug)
        return ultimo_resultado if not self.silent_mode else None

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

        # Concatenación de strings
        if operacion.operador == '+':
            return str(izquierda) + str(derecha)

        # Conversión implícita de tipos
        if isinstance(izquierda, int) and isinstance(derecha, float):
            izquierda = float(izquierda)
        elif isinstance(derecha, int) and isinstance(izquierda, float):
            derecha = float(derecha)

        # Operaciones matemáticas
        if isinstance(izquierda, (int, float)) and isinstance(derecha, (int, float)):
            if operacion.operador == '+':
                return izquierda + derecha
            elif operacion.operador == '-':
                return izquierda - derecha
            elif operacion.operador == '*':
                return izquierda * derecha
            elif operacion.operador == '/':
                return izquierda / derecha
        
        raise ValueError(f"Operación no soportada: {type(izquierda)} {operacion.operador} {type(derecha)}")
        
        
    def evaluar_expresion(self, expr, debug=False):
        if debug:
            print(f"Evaluando expresión: {expr}")

        if isinstance(expr, Numero):
            return expr.valor
        elif isinstance(expr, Variable):
            if expr.nombre not in self.memoria:
                raise NameError(f"Variable no definida: '{expr.nombre}'")
            return self.memoria[expr.nombre]
        elif isinstance(expr, Cadena):
            return expr.valor
        elif isinstance(expr, OperacionBinaria):
            izquierda = self.evaluar_expresion(expr.izquierda, debug)
            derecha = self.evaluar_expresion(expr.derecha, debug)
            
            if debug:
                print(f"Operación: {izquierda} {expr.operador} {derecha}")
            
            # Operaciones aritméticas
            if expr.operador == '+':
                if isinstance(izquierda, (int, float)) and isinstance(derecha, (int, float)):
                    return izquierda + derecha
                return str(izquierda) + str(derecha)
            elif expr.operador == '-':
                return izquierda - derecha
            elif expr.operador == '*':
                return izquierda * derecha
            elif expr.operador == '/':
                return izquierda / derecha
            # Operaciones de comparación
            elif expr.operador == '<':
                return izquierda < derecha
            elif expr.operador == '<=':
                return izquierda <= derecha
            elif expr.operador == '>':
                return izquierda > derecha
            elif expr.operador == '>=':
                return izquierda >= derecha
            elif expr.operador == '=':
                return izquierda == derecha
            elif expr.operador in ('!=', '<>'):
                return izquierda != derecha
            elif expr.operador == '==':
                return izquierda == derecha
            # Operaciones lógicas
            elif expr.operador == 'and':
                return izquierda and derecha
            elif expr.operador == 'or':
                return izquierda or derecha
            elif expr.operador == 'not':
                return izquierda or derecha
            # Condicionales
            elif isinstance(expr, If):
                return self.evaluar_if(expr, debug)
            elif isinstance(expr, Bloque):
                return self.evaluar_bloque(expr, debug)
            else:
                raise ValueError(f"Operador no soportado: {expr.operador}")
        elif isinstance(expr, OperacionUnaria):
            valor = self.evaluar_expresion(expr.expresion, debug)
            if debug:
                print(f"Operación unaria: {expr.operador} {valor}")
            if expr.operador == 'not':
                return not valor
            else:
                raise ValueError(f"Operador unario no soportado: {expr.operador}")
        else:
            raise ValueError(f"Tipo de expresión no soportada: {type(expr)}")

    def evaluar_if(self, nodo_if, debug=False):
        if debug:
            print(f"\n[DEBUG] Evaluando condición IF: {nodo_if.condicion}")
        
        condicion = self.evaluar_expresion(nodo_if.condicion, debug)
        
        if debug:
            print(f"[DEBUG] Resultado condición: {condicion}")
            print(f"[DEBUG] Cuerpo IF contiene {len(nodo_if.cuerpo)} declaraciones")
        
        if condicion:
            if debug:
                print(f"[DEBUG] Ejecutando bloque if con {len(nodo_if.cuerpo)} declaraciones")
            for declaracion in nodo_if.cuerpo:
                self.ejecutar([declaracion], debug)
        
        return None
            

    def evaluar_bloque(self, bloque, debug=False):
        resultado = None
        for declaracion in bloque.declaraciones:
            resultado = self.ejecutar([declaracion], debug)
        return resultado
    
    def imprimir_memoria(self):
        """Muestra las variables con colores"""
        if not self.memoria:
            print("(no hay variables definidas)")
            return
            
        max_len = max(len(var) for var in self.memoria.keys()) if self.memoria else 0
        
        for var, valor in sorted(self.memoria.items()):
            var_padded = var.ljust(max_len)
            if isinstance(valor, (int, float)):
                print(f"{Colors.VARIABLE}{var_padded}{Colors.RESET}: {Colors.NUMERO}{valor}{Colors.RESET}")
            elif isinstance(valor, bool):
                print(f"{Colors.VARIABLE}{var_padded}{Colors.RESET}: {Colors.BOOL}{valor}{Colors.RESET}")
            else:
                print(f"{Colors.VARIABLE}{var_padded}{Colors.RESET}: {valor}")
