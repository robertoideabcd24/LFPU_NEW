from base import Numero, Variable, OperacionBinaria, Asignacion, Prt, Cadena, OperacionUnaria, Booleano, If, Bloque, Clase, CreacionInstancia, InstanciaClase, Atributo, AsignacionAtributo, Fac, Sqrt, Pow, Inp, Rnd
# convertir la lista de tokens en un AST (Árbol de Sintaxis Abstracta)
class Parser:
   
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0
        self.debug = False
        self.nivel_actual = 0
        self.pila_indentacion = [0]
        self._en_estructura_control = False 

    def analizar(self):
        declaraciones = []
        
        while self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            declaracion = None
            
            # Saltar indentación no esperada (no en bloques de control)
            if token_actual[0] == 'INDENTACION' and not self._en_estructura_control:
                self.posicion += 1
                continue
                
            # Manejo de nueva línea
            if token_actual[0] == 'NUEVA_LINEA':
                self.posicion += 1
                continue
                
            # Procesar declaraciones
            if token_actual[0] == 'ID' and self._verificar_tipo_siguiente('ASIGNACION'):
                declaracion = self.declaracion_asignacion()
                
            elif self._verificar('PRT'):
                declaracion = self.declaracion_prt()
                
            elif self._verificar('IF'):
                self._en_estructura_control = True
                declaracion = self.declaracion_if()
                self._en_estructura_control = False
                
            elif self._verificar('ELIF') or self._verificar('ELSE'):
                raise SyntaxError(f"'{token_actual[1]}' fuera de bloque if")
                
            elif token_actual[0] == 'PUNTO_COMA':
                self.posicion += 1
                continue
                
            else:
                raise SyntaxError(f"Token inesperado: {token_actual[1]}")

            if declaracion:
                declaraciones.append(declaracion)
        
        return declaraciones
    
    def _manejar_indentacion(self, nivel):
        if nivel > self.pila_indentacion[-1]:
            # Aumento de indentación
            self.pila_indentacion.append(nivel)
        elif nivel < self.pila_indentacion[-1]:
            # Disminución de indentación
            self.pila_indentacion.pop()
        self.posicion += 1

    def declaracion(self):

        if self._verificar('CLASS'):
            return self.declaracion_clase()
        elif (self._verificar('ID') and 
            self._verificar_tipo_siguiente('DOS_PUNTOS') and 
            self._verificar_posicion(2, 'ASIGNACION')):
            return self.creacion_instancia()
        elif self._verificar('ID') and self._verificar_tipo_siguiente('ASIGNACION'):
            return self.asignacion()
        elif self._verificar('PRT'):
            return self.declaracion_prt()
        elif self._verificar('FAC'):
            return self.declaracion_fac()
        elif self._verificar('SQRT'):
            return self.declaracion_sqrt()
        else:
            return self.expresion()
        
    def creacion_instancia(self):
        nombre_instancia = self._consumir('ID', "Se esperaba nombre de instancia")
        self._consumir('DOS_PUNTOS', "Se esperaba ':'")
        self._consumir('ASIGNACION', "Se esperaba ':='")
        nombre_clase = self._consumir('ID', "Se esperaba nombre de clase")
        self._consumir('PAREN_IZQ', "Se esperaba '('")
        self._consumir('PAREN_DER', "Se esperaba ')'")
        self._consumir('PUNTO_COMA', "Se esperaba ';'")
        return CreacionInstancia(nombre_instancia, nombre_clase)

    def declaracion_prt(self):
        self.posicion += 1  # Consumir 'Prt'
        
        # Verificar paréntesis
        if not self._verificar('PAREN_IZQ'):
            raise SyntaxError("Se esperaba '(' después de Prt")
        self.posicion += 1
        
        expresion = self.expresion()
        
        if not self._verificar('PAREN_DER'):
            raise SyntaxError("Se esperaba ')' después de expresión")
        self.posicion += 1
        
        # Punto y coma opcional
        if self._verificar('PUNTO_COMA'):
            self.posicion += 1
        
        return Prt(expresion)


    def expresion(self):
        return self.expresion_suma()

    def expresion_suma(self):
        nodo = self.expresion_multiplicacion()
        while self.posicion < len(self.tokens) and self.tokens[self.posicion][0] in ('SUMA', 'RESTA'):
            operador = self.tokens[self.posicion][1]
            self.posicion += 1
            nodo = OperacionBinaria(nodo, operador, self.expresion_multiplicacion())
        return nodo

    def expresion_multiplicacion(self):
        nodo = self.expresion_funciones()
        while self.posicion < len(self.tokens) and self.tokens[self.posicion][0] in ('MULT', 'DIV'):
            operador = self.tokens[self.posicion][1]
            self.posicion += 1
            nodo = OperacionBinaria(nodo, operador, self.expresion_funciones())
        return nodo

    def expresion_funciones(self):
        if self._verificar('POW'):
            return self.declaracion_pow()
        elif self._verificar('FAC'):
            return self.declaracion_fac()
        elif self._verificar('SQRT'):
            return self.declaracion_sqrt()
        else:
            return self.factor()
    
    # crea nodos binarios para operaciones de comparación
    def expresion_comparacion(self):
        nodo = self.termino()
        
        while self.posicion < len(self.tokens) and self.tokens[self.posicion][0] in (
            'MENOR', 'MENOR_IGUAL', 'MAYOR', 'MAYOR_IGUAL', 'IGUAL_IGUAL', 'DIFERENTE'
        ):
            operador = self.tokens[self.posicion][1]
            self.posicion += 1
            nodo = OperacionBinaria(nodo, operador, self.termino())
        
        return nodo
    
    # crea nodos binarios para operaciones lógicas
    def expresion_or(self):
        nodo = self.expresion_and()
        
        while self.posicion < len(self.tokens) and self.tokens[self.posicion][0] == 'OR':
            operador = self.tokens[self.posicion][1]
            self.posicion += 1
            nodo = OperacionBinaria(nodo, operador, self.expresion_and())
        
        return nodo

    # crea nodos binarios para operaciones lógicas
    def expresion_and(self):
        nodo = self.expresion_not()
        
        while self.posicion < len(self.tokens) and self.tokens[self.posicion][0] == 'AND':
            operador = self.tokens[self.posicion][1]
            self.posicion += 1
            nodo = OperacionBinaria(nodo, operador, self.expresion_not())
        
        return nodo

    # crea nodos unarios para operaciones lógicas
    def expresion_not(self):
        if self.posicion < len(self.tokens) and self.tokens[self.posicion][0] == 'NOT':
            operador = self.tokens[self.posicion][1]
            self.posicion += 1
            # se cambia de recursión a expresion_comparacion
            expresion = self.expresion_not()  
            return OperacionUnaria(operador, expresion)
        return self.expresion_comparacion()
    

    #implementacion para la mayor procedencia de los operadores
    # construccion de nodos para operaciones binarias
    def termino(self):
        nodo = self.factor()  # factor() debe manejar Pow()

        while self.posicion < len(self.tokens) and self.tokens[self.posicion][0] in ('MULT', 'DIV'):
            operador = self.tokens[self.posicion][1]
            self.posicion += 1
            derecho = self.factor()  # Llama a factor() no a termino()
            nodo = OperacionBinaria(nodo, operador, derecho)
        
        return nodo
    
    # cuerpo, identacion y estructura del bloque
    # creacion de nodos para bloques
    def bloque(self):
        declaraciones = []
        # Saltar líneas vacías al inicio
        while self.posicion < len(self.tokens) and self.tokens[self.posicion][0] == 'NUEVA_LINEA':
            self.posicion += 1
        
        # Procesar declaraciones hasta encontrar una línea no indentada
        while self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            
            # Fin del bloque cuando encontramos una línea vacía o menos indentada
            if token_actual[0] == 'NUEVA_LINEA':
                self.posicion += 1
                # Verificar si la siguiente línea está menos indentada
                break
                
            # Parsear declaraciones
            if token_actual[0] == 'PRT':
                declaracion = self.declaracion_prt()
                if declaracion:
                    declaraciones.append(declaracion)
            elif token_actual[0] == 'PUNTO_COMA':
                self.posicion += 1
            else:
                break
                
        return declaraciones
    
    # estructura del bloque con ; 
    def procesar_bloque(self):
        declaraciones = []
        if self.tokens[self.posicion][0] == 'ID':
            declaracion = self.declaracion_asignacion()
            if declaracion:
                declaraciones.append(declaracion)
        elif self.tokens[self.posicion][0] == ';':
            self.posicion += 1
        else:
            self.posicion += 1
        
        return declaraciones
    
    # estructura para las asigancion :=
    # creacion de nodos para asignaciones
    def declaracion_asignacion(self):
        """Maneja asignaciones normales, de atributos y creaciones de instancia"""
        try:
            # Verificar que tenemos suficientes tokens
            if self.posicion + 2 >= len(self.tokens):
                raise SyntaxError("Asignación incompleta")

            # Verificar identificador inicial
            if self.tokens[self.posicion][0] != 'ID':
                raise SyntaxError("Se esperaba un identificador al inicio de asignación")
            
            nombre_var = self.tokens[self.posicion][1]
            self.posicion += 1

            # Verificar si es asignación de atributo
            if (self.posicion < len(self.tokens) and (self.tokens[self.posicion][0] == 'PUNTO')):
                self.posicion += 1  # Consume el punto
                
                if (self.posicion >= len(self.tokens)) or (self.tokens[self.posicion][0] != 'ID'):
                    raise SyntaxError("Se esperaba nombre de atributo después de '.'")
                
                nombre_atrib = self.tokens[self.posicion][1]
                self.posicion += 1

                if (self.posicion >= len(self.tokens)) or (self.tokens[self.posicion][0] != 'ASIGNACION'):
                    raise SyntaxError("Se esperaba ':=' en asignación de atributo")
                
                self.posicion += 1
                valor = self.expresion()
                
                # Punto y coma opcional
                if (self.posicion < len(self.tokens)) and (self.tokens[self.posicion][0] == 'PUNTO_COMA'):
                    self.posicion += 1

                return AsignacionAtributo(nombre_var, nombre_atrib, valor)

            # Verificar operador de asignación
            if (self.posicion >= len(self.tokens)) or (self.tokens[self.posicion][0] != 'ASIGNACION'):
                raise SyntaxError("Se esperaba ':=' en asignación")
            
            self.posicion += 1

            # Verificar si es instanciación (p := Clase())
            if (self.posicion + 2 < len(self.tokens)) and \
            (self.tokens[self.posicion][0] == 'ID') and \
            (self.tokens[self.posicion+1][0] == 'PAREN_IZQ') and \
            (self.tokens[self.posicion+2][0] == 'PAREN_DER'):
                
                nombre_clase = self.tokens[self.posicion][1]
                self.posicion += 3  # Consume ID, (, )
                
                # Punto y coma opcional
                if (self.posicion < len(self.tokens)) and (self.tokens[self.posicion][0] == 'PUNTO_COMA'):
                    self.posicion += 1
                    
                return CreacionInstancia(nombre_var, nombre_clase)

            # Verificar si es una función Sqrt()
            if self._verificar('SQRT'):
                valor = self.declaracion_sqrt()
            else:
                # Asignación normal (x := 5)
                valor = self.expresion()
            
            # Punto y coma opcional
            if (self.posicion < len(self.tokens)) and (self.tokens[self.posicion][0] == 'PUNTO_COMA'):
                self.posicion += 1
                
            return Asignacion(nombre_var, valor)

        except IndexError:
            raise SyntaxError("Asignación incompleta - faltan tokens")

    # obtiene el numero de linea d eun token de forma axuliar
    def get_line_number(self, token_pos):
        """
        Mapea la posición del token en la lista de tokens al número de línea del código fuente.
        Suponemos que cada token tiene información de la línea en su tercer elemento.
        """
        if 0 <= token_pos < len(self.tokens):
            return self.tokens[token_pos][2]  # Suponiendo que cada token es una tupla (tipo, valor, línea)
        return "desconocida"
    
    # combinacion de cadenas y concatenacion
    def optimizar_concatenacion(self, nodo):
        if isinstance(nodo, OperacionBinaria) and nodo.operador == '+':
            # Optimizar recursivamente ambos lados
            izquierda = self.optimizar_concatenacion(nodo.izquierda)
            derecha = self.optimizar_concatenacion(nodo.derecha)
            
            # Caso 1: Ambos son cadenas literales
            if isinstance(izquierda, Cadena) and isinstance(derecha, Cadena):
                return Cadena(izquierda.valor + derecha.valor)
                
            # Caso 2: Izquierda es cadena y derecha es variable/número
            if isinstance(izquierda, Cadena):
                return OperacionBinaria(izquierda, '+', derecha)
                
            # Caso 3: Concatenación múltiple
            if isinstance(izquierda, OperacionBinaria) and izquierda.operador == '+':
                return OperacionBinaria(izquierda, '+', derecha)
                
            return OperacionBinaria(izquierda, nodo.operador, derecha)
        return nodo
   
    def declaracion_if(self):
        """Maneja estructuras if-elif-else con indentación"""
        self._en_estructura_control = True
        try:
            # Consumir 'If'
            self.posicion += 1
            
            # Manejar condición
            self._consumir('PAREN_IZQ', "Se esperaba '(' después de 'if'")
            condicion = self.expresion_or()
            self._consumir('PAREN_DER', "Se esperaba ')' después de condición if")
            self._consumir('DOS_PUNTOS', "Se esperaba ':' después de condición if")
            
            # Manejar indentación
            self._saltar_nuevas_lineas()
            if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'INDENTACION':
                raise SyntaxError("Se esperaba indentación después de if")
            nivel_indentacion = self.tokens[self.posicion][1]
            self.posicion += 1
            
            # Procesar cuerpo del if
            cuerpo_if = []
            while self.posicion < len(self.tokens):
                # Verificar fin del bloque (indentación menor)
                if (self.tokens[self.posicion][0] == 'INDENTACION' and 
                    self.tokens[self.posicion][1] < nivel_indentacion):
                    break
                    
                # Verificar elif/else
                if self.tokens[self.posicion][0] in ('ELIF', 'ELSE'):
                    break
                    
                # Saltar indentación del nivel actual
                if self.tokens[self.posicion][0] == 'INDENTACION':
                    if self.tokens[self.posicion][1] != nivel_indentacion:
                        raise SyntaxError("Indentación inconsistente en bloque if")
                    self.posicion += 1
                    continue
                    
                # Procesar declaración
                if self._verificar('PRT'):
                    declaracion = self.declaracion_prt()
                elif self._verificar('IF'):
                    declaracion = self.declaracion_if()
                elif self._verificar('ID') and self._verificar_tipo_siguiente('ASIGNACION'):
                    declaracion = self.declaracion_asignacion()
                else:
                    break
                    
                if declaracion:
                    cuerpo_if.append(declaracion)
            
            # Procesar ELIFs
            elifs = []
            while self._verificar('ELIF'):
                self.posicion += 1
                self._consumir('PAREN_IZQ', "Se esperaba '(' después de 'elif'")
                cond = self.expresion_or()
                self._consumir('PAREN_DER', "Se esperaba ')' después de condición elif")
                self._consumir('DOS_PUNTOS', "Se esperaba ':' después de condición elif")
                
                self._saltar_nuevas_lineas()
                if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'INDENTACION':
                    raise SyntaxError("Se esperaba indentación en elif")
                nivel = self.tokens[self.posicion][1]
                self.posicion += 1
                
                # Procesar cuerpo elif
                cuerpo_elif = []
                while self.posicion < len(self.tokens):
                    if (self.tokens[self.posicion][0] == 'INDENTACION' and 
                        self.tokens[self.posicion][1] < nivel_indentacion):
                        break
                        
                    if self.tokens[self.posicion][0] in ('ELIF', 'ELSE'):
                        break
                        
                    if self.tokens[self.posicion][0] == 'INDENTACION':
                        if self.tokens[self.posicion][1] != nivel_indentacion:
                            raise SyntaxError("Indentación inconsistente en elif")
                        self.posicion += 1
                        continue
                        
                    # Procesar declaración
                    if self._verificar('PRT'):
                        declaracion = self.declaracion_prt()
                    elif self._verificar('IF'):
                        declaracion = self.declaracion_if()
                    elif self._verificar('ID') and self._verificar_tipo_siguiente('ASIGNACION'):
                        declaracion = self.declaracion_asignacion()
                    else:
                        break
                        
                    if declaracion:
                        cuerpo_elif.append(declaracion)
                
                elifs.append((cond, cuerpo_elif))
            
            # Procesar ELSE
            else_cuerpo = []
            if self._verificar('ELSE'):
                self.posicion += 1
                self._consumir('DOS_PUNTOS', "Se esperaba ':' después de else")
                
                self._saltar_nuevas_lineas()
                if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'INDENTACION':
                    raise SyntaxError("Se esperaba indentación en else")
                nivel = self.tokens[self.posicion][1]
                self.posicion += 1
                
                # Procesar cuerpo else
                while self.posicion < len(self.tokens):
                    if (self.tokens[self.posicion][0] == 'INDENTACION' and 
                        self.tokens[self.posicion][1] < nivel_indentacion):
                        break
                        
                    if self.tokens[self.posicion][0] == 'INDENTACION':
                        if self.tokens[self.posicion][1] != nivel_indentacion:
                            raise SyntaxError("Indentación inconsistente en else")
                        self.posicion += 1
                        continue
                        
                    # Procesar declaración
                    if self._verificar('PRT'):
                        declaracion = self.declaracion_prt()
                    elif self._verificar('IF'):
                        declaracion = self.declaracion_if()
                    elif self._verificar('ID') and self._verificar_tipo_siguiente('ASIGNACION'):
                        declaracion = self.declaracion_asignacion()
                    else:
                        break
                        
                    if declaracion:
                        else_cuerpo.append(declaracion)
            
            return If(condicion, cuerpo_if, elifs, else_cuerpo)
        
        finally:
            self._en_estructura_control = False
    
    def _procesar_bloque_if(self, nivel_esperado):
        """Procesa un bloque indentado dentro de una estructura if"""
        declaraciones = []
        
        while self.posicion < len(self.tokens):
            # Verificar fin del bloque (menor indentación)
            if (self._verificar('INDENTACION') and 
                self.tokens[self.posicion][1] < nivel_esperado):
                break
                
            # Saltar indentación del nivel actual
            if self._verificar('INDENTACION'):
                if self.tokens[self.posicion][1] != nivel_esperado:
                    raise SyntaxError(f"Indentación inconsistente. Esperaba {nivel_esperado}, obtuvo {self.tokens[self.posicion][1]}")
                self.posicion += 1
                continue
                
            # Procesar declaraciones dentro del bloque
            declaracion = self.declaracion()
            if declaracion:
                declaraciones.append(declaracion)
        
        return declaraciones
    
    def _saltar_nuevas_lineas(self):
        while self.posicion < len(self.tokens) and self.tokens[self.posicion][0] in ('NUEVA_LINEA', 'ESPACIO'):
            self.posicion += 1

    def _bloque_en_indentacion(self, nivel_indentacion):
        cuerpo = []
        while self.posicion < len(self.tokens):
            token = self.tokens[self.posicion]

            if token[0] == 'INDENTACION':
                if token[1] < nivel_indentacion:
                    break
                elif token[1] > nivel_indentacion:
                    raise SyntaxError("Indentación inconsistente")
                else:
                    self.posicion += 1
            elif token[0] in ('NUEVA_LINEA', 'ESPACIO'):
                self.posicion += 1
                continue

            if self._verificar('PRT'):
                cuerpo.append(self.declaracion_prt())
            elif self._verificar('IF'):
                cuerpo.append(self.declaracion_if())
            else:
                break

        return cuerpo


    def _procesar_bloque(self, nivel_esperado):
        """Procesa un bloque de código con el nivel de indentación especificado"""
        declaraciones = []
        
        while self.posicion < len(self.tokens):
            # Verificar fin del bloque
            if self._verificar('INDENTACION') and self.tokens[self.posicion][1] < nivel_esperado:
                break
                
            # Saltar indentación del nivel actual
            if self._verificar('INDENTACION'):
                if self.tokens[self.posicion][1] != nivel_esperado:
                    raise SyntaxError("Indentación inconsistente")
                self.posicion += 1
                continue
                
            # Procesar declaraciones
            if self._verificar('PRT'):
                declaraciones.append(self.declaracion_prt())
            elif self._verificar('IF'):
                declaraciones.append(self.declaracion_if())
            elif self._verificar('ID') and self._verificar_tipo_siguiente('ASIGNACION'):
                declaraciones.append(self.declaracion_asignacion())
            else:
                break
                
        return declaraciones



    def _verificar(self, tipo):
        """Verifica si el token actual es del tipo especificado"""
        return self.posicion < len(self.tokens) and self.tokens[self.posicion][0] == tipo
    
    def _verificar_tipo_siguiente(self, tipo):
        """Verifica si el siguiente token es del tipo especificado"""
        return self.posicion + 1 < len(self.tokens) and self.tokens[self.posicion + 1][0] == tipo

    def _es_parte_de_bloque(self):
        """Determina si el token actual es parte de un bloque (If, Eli, Els)"""
        return self.tokens[self.posicion][0] in ('IF', 'ELIF', 'ELSE', 'PRT')
    
    
    def declaracion_clase(self):
        self._consumir('CLASS', "Se esperaba 'Class'")
        nombre_clase = self._consumir('ID', "Se esperaba nombre de clase")
        self._consumir('DOS_PUNTOS', "Se esperaba ':'")
        
        atributos = []
        
        # Leer atributos mientras haya indentación
        while self.posicion < len(self.tokens):
            token = self.tokens[self.posicion]
            
            # Si no hay indentación, terminó la clase
            if token[0] != 'INDENTACION':
                break
            
            self.posicion += 1  # Saltamos la indentación

            # Validamos que haya un ID (atributo)
            if self.tokens[self.posicion][0] != 'ID':
                raise SyntaxError("Se esperaba nombre de atributo en clase")
            
            nombre_atributo = self.tokens[self.posicion][1]
            self.posicion += 1
            
            if self.tokens[self.posicion][0] != 'PUNTO_COMA':
                raise SyntaxError("Se esperaba ';' después de atributo")
            
            self.posicion += 1
            atributos.append(Atributo(nombre_atributo))
        
        return Clase(nombre_clase, atributos)



    def _consumir(self, tipo, mensaje_error):
        """Consume un token del tipo esperado o lanza un error"""
        if self.posicion >= len(self.tokens):
            raise SyntaxError(f"{mensaje_error}. No hay más tokens")
        token_tipo, token_valor = self.tokens[self.posicion]
        if token_tipo != tipo:
            raise SyntaxError(f"{mensaje_error}. Se encontró: {token_tipo}")
        self.posicion += 1
        return token_valor
    
    def _verificar(self, tipo):
        """Verifica si el siguiente token es del tipo dado"""
        if self.posicion < len(self.tokens):
            return self.tokens[self.posicion][0] == tipo
        return False
    
    def _consumir_opcional(self, tipo):
        """Consume el token si es del tipo esperado"""
        if self._verificar(tipo):
            self.posicion += 1
            return True
        return False
    
    def _error_sintaxis(self, mensaje, token_actual=None):
        if token_actual is None and self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
        
        linea = token_actual[2] if len(token_actual) > 2 else "desconocida"
        valor = token_actual[1] if token_actual else "EOF"
        
        raise SyntaxError(f"Error de sintaxis en línea {linea}: {mensaje}. Token inesperado: '{valor}'")
    
    def _esperar(self, tipo, mensaje_error):
        """Consume un token del tipo esperado o lanza un error descriptivo"""
        if self.posicion >= len(self.tokens):
            raise SyntaxError(f"{mensaje_error}. No hay más tokens disponibles")
        
        token = self.tokens[self.posicion]
        if token[0] != tipo:
            raise SyntaxError(f"{mensaje_error}. Se encontró: {token[0]} (valor: '{token[1]}')")
        
        self.posicion += 1
        return token
    
    def declaracion_fac(self):
        self.posicion += 1  # Consumir 'Fac'
        
        if not self._verificar('PAREN_IZQ'):
            raise SyntaxError("Se esperaba '(' después de Fac")
        self.posicion += 1
        
        expresion = self.expresion()
        
        if not self._verificar('PAREN_DER'):
            raise SyntaxError("Se esperaba ')' después de expresión")
        self.posicion += 1
        
        return Fac(expresion)

    def declaracion_sqrt(self):
        self.posicion += 1  # Consumir 'Sqrt'
        
        if not self._verificar('PAREN_IZQ'):
            raise SyntaxError("Se esperaba '(' después de Sqrt")
        self.posicion += 1
        
        expresion = self.expresion()
        
        if not self._verificar('PAREN_DER'):
            raise SyntaxError("Se esperaba ')' después de expresión")
        self.posicion += 1
        
        return Sqrt(expresion)
    
    def declaracion_pow(self):
        """Versión mejorada que maneja expresiones complejas"""
        self.posicion += 1  # Consumir 'Pow'
        self._consumir('PAREN_IZQ', "Se esperaba '(' después de Pow")
        
        # Permite expresiones completas como base
        base = self.expresion()
        
        self._consumir('COMA', "Se esperaba ',' entre base y exponente")
        
        # Permite expresiones completas como exponente
        exponente = self.expresion()
        
        self._consumir('PAREN_DER', "Se esperaba ')' al final de Pow")
        
        return Pow(base, exponente)

    def factor(self):
        if self.posicion >= len(self.tokens):
            raise SyntaxError("Expresión incompleta - se esperaba más tokens")
    
        token = self.tokens[self.posicion]

        if self._verificar('FAC'):
            self.posicion += 1
            if not self._verificar('PAREN_IZQ'):
                raise SyntaxError("Se esperaba '(' después de Fac")
            self.posicion += 1
            expresion = self.expresion()
            if not self._verificar('PAREN_DER'):
                raise SyntaxError("Se esperaba ')' después de expresión en Fac")
            self.posicion += 1
            return Fac(expresion) 
        
        if self._verificar('POW'):
            return self.declaracion_pow()
        
        if self._verificar('RND'):
            self.posicion += 1
            self._consumir('PAREN_IZQ', "Se esperaba '(' después de Rnd")
            
            # Verificar si hay parámetros
            if not self._verificar('PAREN_DER'):
                min_expr = self.expresion()  # Devuelve un nodo (Numero, Variable, etc)
                
                if self._verificar('COMA'):
                    self.posicion += 1
                    max_expr = self.expresion()
                    self._consumir('PAREN_DER', "Se esperaba ')' después de Rnd")
                    return Rnd(min_expr, max_expr)
                else:
                    self._consumir('PAREN_DER', "Se esperaba ')' después de Rnd")
                    return Rnd(Numero(0), min_expr)  # Envuelve el 0 en un nodo Numero
            else:
                self.posicion += 1
                return Rnd()
        
        if token[0] == 'ENTERO':
            valor = int(self.tokens[self.posicion][1])
            self.posicion += 1
            return Numero(valor)
        
        elif token[0] == 'FLOTANTE':
            self.posicion += 1
            return Numero(float(token[1]))
        
        elif token[0] == 'ID':
            
            if token[1].lower() == 'true':
                self.posicion += 1
                return Booleano(True)
            elif token[1].lower() == 'false':
                self.posicion += 1
                return Booleano(False)
            self.posicion += 1
            return Variable(token[1])
        
        elif token[0] == 'CADENA':
            self.posicion += 1
            return Cadena(token[1])
        
        elif token[0] == 'BOOLEANO':
            self.posicion += 1
            return Booleano(token[1])
        
        elif token[0] == 'PAREN_IZQ':
            self.posicion += 1
            nodo = self.expresion()
            if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'PAREN_DER':
                raise SyntaxError("Error: Se esperaba ')'")
            self.posicion += 1
            return nodo
        
        elif token[0] == 'RESTA':
            self.posicion += 1
            return OperacionBinaria(Numero(0), '-', self.factor())
        
        elif self._verificar('INP'):
            self.posicion += 1  # Consumir 'Inp'
            
            # Manejar Inp con mensaje opcional: Inp("Introduce tu nombre:")
            mensaje = None
            if self._verificar('PAREN_IZQ'):
                self.posicion += 1
                if not self._verificar('PAREN_DER'):  # Si hay algo dentro de los paréntesis
                    mensaje = self.expresion()
                self._consumir('PAREN_DER', "Se esperaba ')' después de Inp")
            
            return Inp(mensaje)

        else:
            # Provide more context in the error message
            line = self.get_line_number(self.posicion)
            raise SyntaxError(
                f"Error en línea {line}: Token inesperado '{token[1]}' ({token[0]}). "
                f"Se esperaba un número, variable, cadena o expresión entre paréntesis"
            )