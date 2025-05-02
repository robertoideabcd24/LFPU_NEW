from base import Numero, Variable, OperacionBinaria, Asignacion, Prt, Cadena, OperacionUnaria, Booleano, If, Bloque, Clase, CreacionInstancia, InstanciaClase, Atributo, AsignacionAtributo
# convertir la lista de tokens en un AST (Árbol de Sintaxis Abstracta)
class Parser:
   
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0
        self.debug = False

    def analizar(self):
        declaraciones = []
        
        while self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            
            # Saltar tokens de formato
            if token_actual[0] in ('NUEVA_LINEA', 'ESPACIO', 'TAB', 'PUNTO_COMA'):
                self.posicion += 1
                continue
                
            # Manejar declaraciones de nivel superior (sin indentación)
            if token_actual[0] != 'INDENTACION':
                if token_actual[0] == 'ID':
                    if self.posicion+1 < len(self.tokens) and self.tokens[self.posicion+1][0] == 'ASIGNACION':
                        declaraciones.append(self.declaracion_asignacion())
                    else:
                        self.posicion += 1
                elif token_actual[0] == 'PRT':
                    # Solo procesar PRT no indentado
                    if self.posicion == 0 or self.tokens[self.posicion-1][0] != 'INDENTACION':
                        declaraciones.append(self.declaracion_prt())
                    else:
                        self.posicion += 1
                elif token_actual[0] == 'IF':
                    declaraciones.append(self.declaracion_if())
                else:
                    self.posicion += 1
            else:
                # Indentación inesperada a nivel raíz
                raise SyntaxError(f"Indentación inesperada en posición {self.posicion}")
        
        return declaraciones

   
    def declaracion(self):
        if self._verificar('CLASS'):
            return self.declaracion_clase()
        # Verificar si es una creación de instancia (p := Suma())
        elif (self._verificar('ID') and 
            self._verificar_tipo_siguiente('DOS_PUNTOS') and 
            self._verificar_posicion(2, 'ASIGNACION')):
            return self.creacion_instancia()
        elif self._verificar('ID') and self._verificar_tipo_siguiente('ASIGNACION'):
            return self.asignacion()
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
        if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'PRT':
            return None
            # se comienza a consumir 'Prt'
        self.posicion += 1  
        
        # Verificar paréntesis de apertura
        if self.tokens[self.posicion][0] != 'PAREN_IZQ':
            raise SyntaxError("Se esperaba '(' después de Prt")
        self.posicion += 1
        
        expresion = self.expresion()
        
        # Verificar paréntesis de cierre
        if self.tokens[self.posicion][0] != 'PAREN_DER':
            raise SyntaxError("Se esperaba ')' después de expresión en Prt")
        self.posicion += 1
        
        # Verificar punto y coma final si existe
        if self.posicion < len(self.tokens) and self.tokens[self.posicion][0] == 'PUNTO_COMA':
            self.posicion += 1
            
        return Prt(expresion)


    def expresion(self):
        nodo = self.termino()

        while self.posicion < len(self.tokens) and self.tokens[self.posicion][0] in ('SUMA', 'RESTA', 'MENOR', 'MENOR_IGUAL', 'MAYOR', 'MAYOR_IGUAL', 'IGUAL', 'DIFERENTE'):
            operador = self.tokens[self.posicion][1]
            self.posicion += 1  # Avanzar después del operador
            nodo = OperacionBinaria(nodo, operador, self.termino())

        return nodo
    
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
        nodo = self.factor()

        while self.posicion < len(self.tokens) and self.tokens[self.posicion][0] in ('MULT', 'DIV'):
            token = self.tokens[self.posicion]
            if token[0] == 'MULT':
                self.posicion += 1
                nodo = OperacionBinaria(nodo, '*', self.factor())
            elif token[0] == 'DIV':
                self.posicion += 1
                nodo = OperacionBinaria(nodo, '/', self.factor())
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
        # Verificar que empiece con ID
        if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'ID':
            raise SyntaxError("Se esperaba un identificador")

        # Primer identificador (objeto o variable)
        primer_id = self.tokens[self.posicion][1]
        self.posicion += 1

        # Caso 1: Asignación a atributo (obj.atr := valor)
        if (self.posicion < len(self.tokens) and 
            self.tokens[self.posicion][0] == 'PUNTO'):
            
            self.posicion += 1  # Consume el punto
            
            if (self.posicion >= len(self.tokens) or 
                self.tokens[self.posicion][0] != 'ID'):
                raise SyntaxError("Se esperaba nombre de atributo después de '.'")
            
            nombre_atributo = self.tokens[self.posicion][1]
            self.posicion += 1  # Consume atributo

            if (self.posicion >= len(self.tokens) or 
                self.tokens[self.posicion][0] != 'ASIGNACION'):
                raise SyntaxError("Se esperaba ':=' en asignación de atributo")
            
            self.posicion += 1  # Consume ':='
            valor = self.expresion()

            # Consume ';' si existe
            if (self.posicion < len(self.tokens)) and \
            (self.tokens[self.posicion][0] == 'PUNTO_COMA'):
                self.posicion += 1

            return AsignacionAtributo(primer_id, nombre_atributo, valor)

        # Caso 2: Asignación normal o instanciación
        if (self.posicion >= len(self.tokens) or 
            self.tokens[self.posicion][0] != 'ASIGNACION'):
            raise SyntaxError("Se esperaba ':=' en asignación")
        
        self.posicion += 1  # Consume ':='

        # Caso 2a: Instanciación (p := Suma())
        if (self.posicion + 2 < len(self.tokens)) and \
        (self.tokens[self.posicion][0] == 'ID') and \
        (self.tokens[self.posicion + 1][0] == 'PAREN_IZQ') and \
        (self.tokens[self.posicion + 2][0] == 'PAREN_DER'):
            
            nombre_clase = self.tokens[self.posicion][1]
            self.posicion += 3  # Consume ID, (, )
            
            # Consume punto y coma si existe
            if (self.posicion < len(self.tokens)) and \
            (self.tokens[self.posicion][0] == 'PUNTO_COMA'):
                self.posicion += 1
                
            return CreacionInstancia(primer_id, nombre_clase)

        # Caso 2b: Asignación normal (x := 5)
        valor = self.expresion()
        
        if (self.posicion < len(self.tokens)) and \
        (self.tokens[self.posicion][0] == 'PUNTO_COMA'):
            self.posicion += 1
            
        return Asignacion(primer_id, valor)



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
        if self.debug:
            print(f"[DEBUG IF] Iniciando If en posición {self.posicion}")

        # Consumir 'If'
        self.posicion += 1
        
        # Procesar condición
        if self.tokens[self.posicion][0] != 'PAREN_IZQ':
            raise SyntaxError("Se esperaba '(' después de 'If'")
        self.posicion += 1
        
        condicion = self.expresion_or()
        
        if self.tokens[self.posicion][0] != 'PAREN_DER':
            raise SyntaxError("Se esperaba ')' después de condición If")
        self.posicion += 1
        
        if self.tokens[self.posicion][0] != 'DOS_PUNTOS':
            raise SyntaxError("Se esperaba ':' después de condición If")
        self.posicion += 1
        
        # Procesar indentación del if
        if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'INDENTACION':
            raise SyntaxError("Se esperaba indentación después del if")
        
        nivel_if = int(self.tokens[self.posicion][1])
        self.posicion += 1
        
        # Procesar cuerpo del if (solo declaraciones con mayor indentación)
        cuerpo = []
        while self.posicion < len(self.tokens):
            # Verificar fin de bloque
            if self.tokens[self.posicion][0] == 'INDENTACION':
                current_indent = int(self.tokens[self.posicion][1])
                if current_indent < nivel_if:
                    break
                if current_indent > nivel_if:
                    raise SyntaxError("Indentación inconsistente en bloque if")
                self.posicion += 1
            
            # Procesar declaraciones dentro del if
            token_actual = self.tokens[self.posicion]
            
            if token_actual[0] == 'PRT':
                cuerpo.append(self.declaracion_prt())
            elif token_actual[0] == 'IF':
                cuerpo.append(self.declaracion_if())
            elif token_actual[0] == 'ID' and self.posicion+1 < len(self.tokens) and self.tokens[self.posicion+1][0] == 'ASIGNACION':
                cuerpo.append(self.declaracion_asignacion())
            else:
                break
        
        # Procesar ELIFs
        elifs = []
        while self.posicion < len(self.tokens) and self.tokens[self.posicion][0] == 'ELIF':
            self.posicion += 1  # Consumir 'ELIF'
            
            # Procesar condición ELIF
            if self.tokens[self.posicion][0] != 'PAREN_IZQ':
                raise SyntaxError("Se esperaba '(' después de 'elif'")
            self.posicion += 1
            
            cond_elif = self.expresion_or()
            
            if self.tokens[self.posicion][0] != 'PAREN_DER':
                raise SyntaxError("Se esperaba ')' después de condición elif")
            self.posicion += 1
            
            if self.tokens[self.posicion][0] != 'DOS_PUNTOS':
                raise SyntaxError("Se esperaba ':' después de condición elif")
            self.posicion += 1
            
            # Procesar indentación ELIF
            if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'INDENTACION':
                raise SyntaxError("Se esperaba indentación después de elif")
            
            nivel_elif = int(self.tokens[self.posicion][1])
            self.posicion += 1
            
            # Procesar cuerpo ELIF
            cuerpo_elif = []
            while self.posicion < len(self.tokens):
                if self.tokens[self.posicion][0] == 'INDENTACION':
                    current_indent = int(self.tokens[self.posicion][1])
                    if current_indent < nivel_elif:
                        break
                    if current_indent > nivel_elif:
                        raise SyntaxError("Indentación inconsistente en elif")
                    self.posicion += 1
                
                token_actual = self.tokens[self.posicion]
                
                if token_actual[0] == 'PRT':
                    cuerpo_elif.append(self.declaracion_prt())
                elif token_actual[0] == 'IF':
                    cuerpo_elif.append(self.declaracion_if())
                elif token_actual[0] == 'ID' and self.posicion+1 < len(self.tokens) and self.tokens[self.posicion+1][0] == 'ASIGNACION':
                    cuerpo_elif.append(self.declaracion_asignacion())
                else:
                    break
            
            elifs.append((cond_elif, cuerpo_elif))
        
        # Procesar ELSE
        else_cuerpo = None
        if self.posicion < len(self.tokens) and self.tokens[self.posicion][0] == 'ELSE':
            self.posicion += 1  # Consumir 'ELSE'
            
            if self.tokens[self.posicion][0] != 'DOS_PUNTOS':
                raise SyntaxError("Se esperaba ':' después de 'else'")
            self.posicion += 1
            
            # Procesar indentación ELSE
            if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'INDENTACION':
                raise SyntaxError("Se esperaba indentación después de else")
            
            nivel_else = int(self.tokens[self.posicion][1])
            self.posicion += 1
            
            # Procesar cuerpo ELSE
            else_cuerpo = []
            while self.posicion < len(self.tokens):
                if self.tokens[self.posicion][0] == 'INDENTACION':
                    current_indent = int(self.tokens[self.posicion][1])
                    if current_indent < nivel_else:
                        break
                    if current_indent > nivel_else:
                        raise SyntaxError("Indentación inconsistente en else")
                    self.posicion += 1
                
                token_actual = self.tokens[self.posicion]
                
                if token_actual[0] == 'PRT':
                    else_cuerpo.append(self.declaracion_prt())
                elif token_actual[0] == 'IF':
                    else_cuerpo.append(self.declaracion_if())
                elif token_actual[0] == 'ID' and self.posicion+1 < len(self.tokens) and self.tokens[self.posicion+1][0] == 'ASIGNACION':
                    else_cuerpo.append(self.declaracion_asignacion())
                else:
                    break
        
        return If(condicion, cuerpo, elifs, else_cuerpo)
    
    def _procesar_bloque_indentado(self):
        declaraciones = []
        
        # Verificar si hay indentación
        if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'INDENTACION':
            return declaraciones
        
        nivel_indent = int(self.tokens[self.posicion][1])
        self.posicion += 1  # Consumir indentación
        
        while self.posicion < len(self.tokens):
            # Verificar fin de bloque
            if self.tokens[self.posicion][0] == 'INDENTACION':
                if int(self.tokens[self.posicion][1]) < nivel_indent:
                    break
                self.posicion += 1
            
            # Procesar declaraciones
            token_actual = self.tokens[self.posicion]
            
            if token_actual[0] == 'PRT':
                declaraciones.append(self.declaracion_prt())
            elif token_actual[0] == 'IF':
                declaraciones.append(self.declaracion_if())
            elif token_actual[0] == 'ID' and self.posicion+1 < len(self.tokens) and self.tokens[self.posicion+1][0] == 'ASIGNACION':
                declaraciones.append(self.declaracion_asignacion())
            else:
                break
        
        return declaraciones

    def _verificar_tipo_siguiente(self, tipo):
        """Verifica si el siguiente token es del tipo especificado"""
        return (self.posicion + 1 < len(self.tokens)) and \
            (self.tokens[self.posicion + 1][0] == tipo)

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
    
    def factor(self):
        if self.posicion >= len(self.tokens):
            raise SyntaxError("Expresión incompleta - se esperaba más tokens")
        
        token = self.tokens[self.posicion]
        
        if token[0] == 'ENTERO':
            self.posicion += 1
            return Numero(int(token[1]))
        elif token[0] == 'FLOTANTE':
            self.posicion += 1
            return Numero(float(token[1]))
        elif token[0] == 'ID':
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
        else:
            raise ValueError(f"Token inesperado en factor: {token[0]}")
            
