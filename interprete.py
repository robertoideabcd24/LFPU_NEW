import os
from base import Numero, Variable, OperacionBinaria, Asignacion, Prt, Cadena, OperacionUnaria, If, Bloque, Booleano, Clase, CreacionInstancia, InstanciaClase, ExitCommand, AsignacionAtributo, Fac, Sqrt, Pow, Inp
from flup_logger import BasicFlupLogger, json
from colors import Colors
import math

class Interpreter:
    def __init__(self):
        self.memoria = {}
        self.clases = {}
        self.silent_mode = False
        self.running = True 
        self.logger = BasicFlupLogger() 
        self.ambitos = [{}]

    def ejecutar(self, ast, debug=False):
        self.debug = debug
        self.memoria = {}
        self.clases = {}

        # Asegurarse de que ast sea una lista, incluso si es un solo nodo
        if not isinstance(ast, (list, tuple)):
            ast = [ast]
        
        for nodo in ast:
            try:
                if isinstance(nodo, Prt):
                    valor = self.evaluar_expresion(nodo.expresion)
                    if not self.silent_mode:
                        print(valor)
                    # Registrar en el log
                    self.logger.log_execution(
                        source_code=f"Prt({nodo.expresion})",
                        output=str(valor),
                        metadata={
                            "type": "print",
                            "memory_snapshot": self.memoria.copy()
                        }
                    )

                if isinstance(nodo, Fac):
                    valor = self.evaluar_expresion(nodo.expresion)
                    resultado = self.calcular_factorial(valor)
                    print(resultado) 

                elif isinstance(nodo, Clase):
                    self.clases[nodo.nombre] = nodo
                    if debug:
                        print(f"[DEBUG] Clase definida: {nodo.nombre}")

                elif isinstance(nodo, CreacionInstancia):
                    if nodo.nombre_clase not in self.clases:
                        raise NameError(f"Clase no definida: {nodo.nombre_clase}")
                    
                    # Crear instancia con atributos
                    atributos = {a.nombre: None for a in self.clases[nodo.nombre_clase].atributos}
                    self.memoria[nodo.nombre_instancia] = {
                        '__clase__': nodo.nombre_clase,
                        '__atributos__': atributos
                    }
                    
                    if debug:
                        print(f"[DEBUG] Instancia creada: {nodo.nombre_instancia}")

                elif isinstance(nodo, AsignacionAtributo):
                    if nodo.objeto not in self.memoria:
                        raise NameError(f"Instancia no existe: {nodo.objeto}")
                    
                    instancia = self.memoria[nodo.objeto]
                    
                    # Verificar que el atributo existe
                    clase = self.clases[instancia['__clase__']]
                    if nodo.atributo not in [a.nombre for a in clase.atributos]:
                        raise AttributeError(f"Atributo no existe: {nodo.atributo}")
                    
                    valor = self.evaluar_expresion(nodo.valor)
                    self.memoria[nodo.nombre_var] = valor
                    self.logger.log_execution(
                        source_code=f"{nodo.nombre_var} := {nodo.valor}",
                        output=f"{nodo.nombre_var} = {valor}",
                        command_type="assignment",
                        metadata={
                            "variable": nodo.nombre_var,
                            "value_type": type(valor).__name__
                        }
                    )
                    
                    if debug:
                        print(f"[DEBUG] Asignado {nodo.objeto}.{nodo.atributo} = {valor}")

                elif isinstance(nodo, If):
                    if debug:
                        print(f"[DEBUG] Evaluando If con condición: {nodo.condicion}")
                    
                    # Guardar estado de memoria antes del bloque condicional
                    memoria_anterior = self.memoria.copy()
                    try:
                        # Evaluar condición principal
                        condicion = self.evaluar_expresion(nodo.condicion, debug)
                        
                        if condicion:
                            if debug:
                                print("[DEBUG] Ejecutando cuerpo If")
                            for stmt in nodo.cuerpo:
                                self.ejecutar([stmt], debug)
                        else:
                            # Procesar ELIFs
                            ejecutado = False
                            for cond, cuerpo in nodo.elifs:
                                if self.evaluar_expresion(cond, debug):
                                    ejecutado = True
                                    if debug:
                                        print("[DEBUG] Ejecutando cuerpo Elif")
                                    for stmt in cuerpo:
                                        self.ejecutar([stmt], debug)
                                    break
                            
                            # Procesar ELSE si no se ejecutó If ni Elifs
                            if not ejecutado and nodo.else_cuerpo:
                                if debug:
                                    print("[DEBUG] Ejecutando cuerpo Else")
                                for stmt in nodo.else_cuerpo:
                                    self.ejecutar([stmt], debug)
                    except Exception as e:
                        # Restaurar memoria en caso de error
                        self.memoria = memoria_anterior
                        raise

                elif isinstance(nodo, Asignacion):
                    valor = self.evaluar_expresion(nodo.valor, debug)
                    self.memoria[nodo.nombre_var] = valor
                    if debug:
                        print(f"[DEBUG] Asignado {nodo.nombre_var} = {valor}")

            except Exception as e:
                if debug:
                    print(f"[ERROR] {str(e)}")
                raise e

        if debug:
            print("\n=== Memoria Final ===")
            for k, v in self.memoria.items():
                print(f"{k}: {v}")
            print("====================")
    


    def entrar_ambito(self):
        """Crea un nuevo ámbito heredando las variables del anterior"""
        self.ambitos.append(self.memoria.copy())

    def salir_ambito(self):
        """Restaura el ámbito anterior"""
        if len(self.ambitos) > 1:
            self.ambitos.pop()
        self.memoria = self.ambitos[-1]

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

        if isinstance(expr, Fac):  # Usando Fac en lugar de FuncionFactorial
            valor = self.evaluar_expresion(expr.expresion, debug)
            if not isinstance(valor, int) or valor < 0:
                raise ValueError("Fac solo acepta enteros positivos")
            return self.calcular_factorial(valor)
        
        if isinstance(expr, Sqrt):
            valor = self.evaluar_expresion(expr.expresion, debug)
            if not isinstance(valor, (int, float)) or valor < 0:
                raise ValueError("Sqrt solo acepta números positivos")
            return math.sqrt(valor)
        
        if isinstance(expr, Pow):
            base = self.evaluar_expresion(expr.base, debug)
            exponente = self.evaluar_expresion(expr.exponente, debug)
            try:
                resultado = base ** exponente
                if debug:
                    print(f"[DEBUG] Calculando {base}^{exponente} = {resultado}")
                return resultado
            except Exception as e:
                raise ValueError(f"Error en Pow: {str(e)}")


        if isinstance(expr, Numero):
            return expr.valor
        
        if isinstance(expr, Booleano):
            return expr.valor
        if isinstance(expr, Variable):
        # Manejar acceso a atributos (ej: p.nombre)
            if '.' in expr.nombre:
                partes = expr.nombre.split('.')
                if len(partes) != 2:
                    raise SyntaxError("Sintaxis inválida para acceso a atributo")
                
                nombre_instancia, nombre_atributo = partes
                if nombre_instancia not in self.memoria:
                    raise NameError(f"Instancia no definida: '{nombre_instancia}'")
                
                instancia = self.memoria[nombre_instancia]
                if not isinstance(instancia, InstanciaClase):
                    raise TypeError(f"'{nombre_instancia}' no es una instancia de clase")
                
                return instancia.atributos.get(nombre_atributo)
            else:
                # Variable normal
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
        
        elif isinstance(expr, Inp):
            # Mostrar mensaje si existe
            if expr.mensaje:
                mensaje = str(self.evaluar_expresion(expr.mensaje, debug))
                print(mensaje, end=' ')  # Mostrar el mensaje sin salto de línea
            # Leer entrada del usuario
            try:
                user_input = input()
                # Intentar convertir a número si es posible
                try:
                    if '.' in user_input:
                        return float(user_input)
                    return int(user_input)
                except ValueError:
                    return user_input  # Devolver como string si no es número
            except EOFError:
                return ""  # Devolver string vacío si hay error de entrada

        else:
            raise ValueError(f"Tipo de expresión no soportada: {type(expr)}")

    def evaluar_if(self, nodo_if, debug=False):
        if debug:
            print(f"\n[DEBUG] Evaluando condición If: {nodo_if.condicion}")
        
        condicion = self.evaluar_expresion(nodo_if.condicion, debug)
        
        if debug:
            print(f"[DEBUG] Resultado condición: {condicion}")
            print(f"[DEBUG] Cuerpo If contiene {len(nodo_if.cuerpo)} declaraciones")
        
        if condicion:
            if debug:
                print(f"[DEBUG] Ejecutando bloque if con {len(nodo_if.cuerpo)} declaraciones")
            # Guardar estado de memoria antes del bloque
            memoria_anterior = self.memoria.copy()
            try:
                for declaracion in nodo_if.cuerpo:
                    self.ejecutar([declaracion], debug)
            except Exception as e:
                # Restaurar memoria en caso de error
                self.memoria = memoria_anterior
                raise
            
            return True
        
        # Procesar ELIFs si la condición principal fue falsa
        for cond, cuerpo in nodo_if.elifs:
            if self.evaluar_expresion(cond, debug):
                memoria_anterior = self.memoria.copy()
                try:
                    for declaracion in cuerpo:
                        self.ejecutar([declaracion], debug)
                except Exception as e:
                    self.memoria = memoria_anterior
                    raise
                return True
        
        # Procesar ELSE si todas las condiciones anteriores fueron falsas
        if nodo_if.else_cuerpo:
            if debug:
                print("[DEBUG] Ejecutando bloque Else")
            memoria_anterior = self.memoria.copy()
            try:
                for declaracion in nodo_if.else_cuerpo:
                    self.ejecutar([declaracion], debug)
            except Exception as e:
                self.memoria = memoria_anterior
                raise
        
        return False
    
    def calcular_factorial(self, n):
        if n == 0:
            return 1
        resultado = 1
        for i in range(1, n + 1):
            resultado *= i
        return resultado

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


    def show_recent_logs(self, lines=10):
        """Muestra los últimos logs registrados"""
        if not os.path.exists(self.logger.current_log_file):
            print("No hay logs registrados")
            return
        
        with open(self.logger.current_log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            for line in all_lines[-lines:]:
                log_entry = json.loads(line)
                print(f"[{log_entry['timestamp']}] {log_entry['command']}")
                if log_entry['output']:
                    print(f"  => {log_entry['output']}")
                if log_entry['error']:
                    print(f"  !!! ERROR: {log_entry['error']['message']}")


