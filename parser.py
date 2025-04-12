from base import Numero, Variable, OperacionBinaria, Asignacion
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0

    def analizar(self):
        declaraciones = []
        while self.posicion < len(self.tokens):
            if self.tokens[self.posicion][0] == 'ID':
                declaracion = self.declaracion_asignacion()
                if declaracion:
                    declaraciones.append(declaracion)
            elif self.tokens[self.posicion][0] == 'PUNTO_COMA':
                self.posicion += 1
            else:
                break
        return declaraciones  # Siempre devuelve una lista

    def expresion(self):
        nodo = self.termino()

        while self.posicion < len(self.tokens) and self.tokens[self.posicion][0] in ('SUMA', 'RESTA'):
            operador = self.tokens[self.posicion][1]
            self.posicion += 1
            nodo = OperacionBinaria(nodo, operador, self.termino())

        return nodo

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
                
            if self.tokens[self.posicion][0] == 'ID' and self.tokens[self.posicion + 1][0] == 'ASIGNACION':
                nombre_var = self.tokens[self.posicion][1]
                self.posicion += 2  # Avanzar sobre ID y ASIGNACION
                
                # Verificar que hay tokens suficientes para la expresión
                if self.posicion >= len(self.tokens):
                    raise SyntaxError("Expresión faltante después de asignación")
                    
                expresion = self.expresion()
                
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

    def factor(self):
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
        elif token[0] == 'PAREN_IZQ':
            self.posicion += 1
            nodo = self.expresion()
            if self.posicion >= len(self.tokens) or self.tokens[self.posicion][0] != 'PAREN_DER':
                raise SyntaxError("Error: Se esperaba ')' para cerrar paréntesis")
            self.posicion += 1
            return nodo
        elif token[0] == 'RESTA':  # Operador unario negativo
            self.posicion += 1
            return OperacionBinaria(Numero(0), '-', self.factor())
        else:
            raise ValueError(f"Token inesperado en factor: {token[0]}")
            
