from base import Numero, Variable, OperacionBinaria, Asignacion, Prt, Cadena, OperacionUnaria, Booleano, If, Bloque
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0

    def analizar(self):
        declaraciones = []
        while self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            
            # Saltar tokens de formato
            if token_actual[0] in ('NUEVA_LINEA', 'ESPACIO', 'TAB', 'PUNTO_COMA'):
                self.posicion += 1
                continue
                
            # Procesar declaraciones
            if token_actual[0] == 'ID':
                # Verificar si es asignación (siguiente token es ASIGNACION)
                if self.posicion + 1 < len(self.tokens) and self.tokens[self.posicion + 1][0] == 'ASIGNACION':
                    declaracion = self.declaracion_asignacion()
                else:
                    declaracion = None
            elif token_actual[0] == 'PRT':
                declaracion = self.declaracion_prt()
            elif token_actual[0] == 'IF':
                declaracion = self.declaracion_if()
            else:
                self.posicion += 1
                continue
                
            if declaracion:
                declaraciones.append(declaracion)
        return declaraciones

    def declaracion_prt(self):
        if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'PRT':
            return None
            
        self.posicion += 1  # Consumir 'Prt'
        
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
    
    def expresion_comparacion(self):
        nodo = self.termino()
        
        while self.posicion < len(self.tokens) and self.tokens[self.posicion][0] in (
            'MENOR', 'MENOR_IGUAL', 'MAYOR', 'MAYOR_IGUAL', 'IGUAL_IGUAL', 'DIFERENTE'
        ):
            operador = self.tokens[self.posicion][1]
            self.posicion += 1
            nodo = OperacionBinaria(nodo, operador, self.termino())
        
        return nodo
    
    def expresion_or(self):
        nodo = self.expresion_and()
        
        while self.posicion < len(self.tokens) and self.tokens[self.posicion][0] == 'OR':
            operador = self.tokens[self.posicion][1]
            self.posicion += 1
            nodo = OperacionBinaria(nodo, operador, self.expresion_and())
        
        return nodo

    def expresion_and(self):
        nodo = self.expresion_not()
        
        while self.posicion < len(self.tokens) and self.tokens[self.posicion][0] == 'AND':
            operador = self.tokens[self.posicion][1]
            self.posicion += 1
            nodo = OperacionBinaria(nodo, operador, self.expresion_not())
        
        return nodo

    def expresion_not(self):
        if self.posicion < len(self.tokens) and self.tokens[self.posicion][0] == 'NOT':
            operador = self.tokens[self.posicion][1]
            self.posicion += 1
            expresion = self.expresion_not()  # Cambiado de recursión a expresion_comparacion
            return OperacionUnaria(operador, expresion)
        return self.expresion_comparacion()

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
    
    
    def declaracion_asignacion(self):
        try:
            if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'ID':
                return None
            
            nombre_var = self.tokens[self.posicion][1]
            self.posicion += 1  # Consumir ID
            
            # Verificar operador de asignación
            if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'ASIGNACION':
                raise SyntaxError(f"Se esperaba ':=' después de '{nombre_var}'")
            self.posicion += 1  # Consumir :=
            
            # Obtener la expresión del valor
            valor = self.expresion()
            
            # Verificar punto y coma final si existe
            if self.posicion < len(self.tokens) and self.tokens[self.posicion][0] == 'PUNTO_COMA':
                self.posicion += 1
                
            return Asignacion(nombre_var, valor)
        except IndexError as e:
            raise SyntaxError(f"Error de sintaxis: estructura incompleta - {str(e)}")


    def get_line_number(self, token_pos):
        """
        Mapea la posición del token en la lista de tokens al número de línea del código fuente.
        Suponemos que cada token tiene información de la línea en su tercer elemento.
        """
        if 0 <= token_pos < len(self.tokens):
            return self.tokens[token_pos][2]  # Suponiendo que cada token es una tupla (tipo, valor, línea)
        return "desconocida"
    
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
        if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'IF':
            return None
            
        self.posicion += 1  # Consumir 'if'
        
        # Verificar paréntesis de apertura
        if self.tokens[self.posicion][0] != 'PAREN_IZQ':
            raise SyntaxError("Se esperaba '(' después de 'if'")
        self.posicion += 1
        
        condicion = self.expresion_or()
        
        # Verificar paréntesis de cierre
        if self.tokens[self.posicion][0] != 'PAREN_DER':
            raise SyntaxError("Se esperaba ')' después de condición if")
        self.posicion += 1
        
        # Verificar dos puntos
        if self.tokens[self.posicion][0] != 'DOS_PUNTOS':
            raise SyntaxError("Se esperaba ':' después de condición if")
        self.posicion += 1
        
        # Saltar espacios y nuevas líneas
        while self.posicion < len(self.tokens) and self.tokens[self.posicion][0] in ('NUEVA_LINEA', 'ESPACIO'):
            self.posicion += 1
        
        # Procesar cuerpo del if
        cuerpo = []
        while self.posicion < len(self.tokens):
            # Fin del bloque si encontramos una línea no indentada
            if self.tokens[self.posicion][0] == 'NUEVA_LINEA':
                self.posicion += 1
                # Verificar si la siguiente línea está menos indentada
                if self.posicion < len(self.tokens) and self.tokens[self.posicion][0] not in ('ESPACIO', 'TAB'):
                    break
                continue
            
            # Procesar declaración PRT
            if self.tokens[self.posicion][0] == 'PRT':
                prt_decl = self.declaracion_prt()
                if prt_decl:
                    cuerpo.append(prt_decl)
            else:
                break
        
        return If(condicion, cuerpo)

    

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
            
