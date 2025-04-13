from base import Numero, Variable, OperacionBinaria, Asignacion, Prt, Cadena
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
            elif isinstance(declaracion, Prt):  # Nueva condición para Prt
                resultado = self.evaluar_expresion(declaracion.expresion, debug)
                print(resultado)
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
        
        try:
        
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
                
                # Manejar operador +
                if expr.operador == '+':
                    # Si ambos son números, sumar
                    if isinstance(izquierda, (int, float)) and isinstance(derecha, (int, float)):
                        return izquierda + derecha
                    # Si alguno es string, concatenar (convirtiendo a string)
                    return str(izquierda) + str(derecha)
                
                # Para otros operadores, deben ser números
                if not isinstance(izquierda, (int, float)) or not isinstance(derecha, (int, float)):
                    raise TypeError(f"Operador {expr.operador} requiere números, no {type(izquierda)} y {type(derecha)}")
                
                # Operaciones matemáticas
                if expr.operador == '-':
                    return izquierda - derecha
                elif expr.operador == '*':
                    return izquierda * derecha
                elif expr.operador == '/':
                    if derecha == 0:
                        raise ValueError("División por cero")
                    return izquierda / derecha
                else:
                    raise ValueError(f"Operador no soportado: {expr.operador}")
            else:
                raise ValueError(f"Tipo de expresión no soportada: {type(expr)}")
        
        except TypeError as e:
            raise TypeError(f"Error de tipos en operación: {str(e)}")
        except ZeroDivisionError:
            raise ValueError("División por cero")
        except Exception as e:
            raise ValueError(f"Error al evaluar expresión: {str(e)}")

    def imprimir_memoria(self):
        """Muestra las variables con colores"""
        if not self.memoria:
            #print("(no hay variables definidas)")
            return
            
        for var, valor in self.memoria.items():
            if isinstance(valor, str):
                # Reemplazar caracteres especiales para visualización
                valor_mostrar = valor.replace('\n', '\\n').replace('\t', '\\t')
                valor_str = f"{Colors.CADENA}'{valor_mostrar}'{Colors.RESET}"
            elif isinstance(valor, (int, float)):
                valor_str = f"{Colors.NUMERO}{valor}{Colors.RESET}"
            else:
                valor_str = str(valor)
                
            print(f"{Colors.VARIABLE}{var}{Colors.RESET}: {valor_str}")
