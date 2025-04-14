from base import Numero, Variable, OperacionBinaria, Asignacion, Prt, Cadena, OperacionUnaria, Booleano
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0

    def analizar(self):
        declaraciones = []
        while self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            
            if token_actual[0] == 'ID':
                declaracion = self.declaracion_asignacion()
            elif token_actual[0] == 'PRT':
                declaracion = self.declaracion_prt()
            elif token_actual[0] == 'PUNTO_COMA':
                self.posicion += 1
                continue
            else:
                break
                
            if declaracion:
                declaraciones.append(declaracion)
        return declaraciones

    def declaracion_prt(self):
        if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'PRT':
            return None
            
        self.posicion += 1  # Consumir 'Prt'
        
        try:
            if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'PAREN_IZQ':
                raise SyntaxError("Se esperaba '(' después de Prt")
                
            self.posicion += 1  # Consumir '('
            
            if self.posicion >= len(self.tokens):
                raise SyntaxError("Expresión faltante después de Prt")
                
            expresion = self.expresion()
            expresion = self.optimizar_concatenacion(expresion)
            
            if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'PAREN_DER':
                raise SyntaxError("Se esperaba ')' después de la expresión en Prt")
                
            self.posicion += 1  # Consumir ')'
            
            if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'PUNTO_COMA':
                raise SyntaxError("Se esperaba ';' al final de la instrucción Prt")
                
            self.posicion += 1  # Consumir ';'
            return Prt(expresion)
            
        except IndexError:
            raise SyntaxError("Expresión incompleta en Prt")

    def expresion(self):
        nodo = self.termino()

        while self.posicion < len(self.tokens) and self.tokens[self.posicion][0] in ('SUMA', 'RESTA', 'MENOR', 'MENOR_IGUAL', 'MAYOR', 'MAYOR_IGUAL', 'IGUAL', 'DIFERENTE'):
            operador = self.tokens[self.posicion][1]
            self.posicion += 1
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
        while self.posicion < len(self.tokens):
            token_actual = self.tokens[self.posicion]
            
            if token_actual[0] == 'ID':
                declaracion = self.declaracion_asignacion()
                if declaracion:
                    declaraciones.append(declaracion)
            elif token_actual[0] == ';':
                self.posicion += 1
            else:
                self.posicion += 1
        
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
            if self.posicion + 1 >= len(self.tokens):
                raise SyntaxError("Asignación incompleta al final del archivo")
            
            # Buscar el token de asignación ignorando espacios
            next_pos = self.posicion + 1
            while next_pos < len(self.tokens) and self.tokens[next_pos][0] == 'PUNTO_COMA':
                next_pos += 1
                
            if (self.tokens[self.posicion][0] == 'ID' and 
                next_pos < len(self.tokens) and 
                self.tokens[next_pos][0] == 'ASIGNACION'):
            
                nombre_var = self.tokens[self.posicion][1]
                self.posicion = next_pos + 1  # Saltar ID y ASIGNACION
                
                # Verificar que hay tokens suficientes para la expresión
                if self.posicion >= len(self.tokens):
                    raise SyntaxError("Expresión faltante después de asignación")
                    
                # Cambiar esto para usar expresion() que maneja operadores lógicos
                expresion = self.expresion_or()  # Usamos expresion_or() que es el nivel más alto de la jerarquía
                
                # Verificar punto y coma
                if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'PUNTO_COMA':
                    raise SyntaxError("Se esperaba ';' después de asignación")
                
                self.posicion += 1
                return Asignacion(nombre_var, expresion)
            
            return None
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
            
