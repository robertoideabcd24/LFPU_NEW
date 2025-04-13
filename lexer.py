import re

class Lexer:
    def __init__(self, texto_entrada, debug=False):  # Asegúrate de incluir debug como parámetro
        self.texto_entrada = texto_entrada
        self.tokens = []
        self.caracter_actual = None
        self.posicion = 0
        self.debug = debug  # Nuevo parámetro para controlar la salida
        self.avanzar()

    def error(self):
        raise Exception(f"Carácter inválido '{self.caracter_actual}' en la posición {self.posicion}")

    def avanzar(self):
        if self.posicion < len(self.texto_entrada):
            self.caracter_actual = self.texto_entrada[self.posicion]
            self.posicion += 1
        else:
            self.caracter_actual = None

    def saltar_espacios(self):
        while self.caracter_actual is not None and self.caracter_actual.isspace():
            self.avanzar()

    def numero(self):
        resultado = ''
        tiene_punto = False
        
        # Manejar signo negativo (si existe)
        if self.caracter_actual == '-':
            resultado += '-'
            self.avanzar()
        
        # Parte entera antes del punto
        while self.caracter_actual and self.caracter_actual.isdigit():
            resultado += self.caracter_actual
            self.avanzar()
        
        # Parte decimal (después del punto)
        if self.caracter_actual == '.':
            tiene_punto = True
            resultado += '.'
            self.avanzar()
            while self.caracter_actual and self.caracter_actual.isdigit():
                resultado += self.caracter_actual
                self.avanzar()
        
        if tiene_punto:
            return ('FLOTANTE', float(resultado))
        else:
            return ('ENTERO', int(resultado))

    def identificador(self):
        resultado = ''
        while self.caracter_actual is not None and (self.caracter_actual.isalnum() or self.caracter_actual == '_'):
            resultado += self.caracter_actual
            self.avanzar()

        reservadas = {
            'prt': 'PRT',
        }
        
        return (reservadas.get(resultado.lower(), 'ID'), resultado)

    def obtener_siguiente_token(self):
        try:
            while self.caracter_actual is not None:
                if self.caracter_actual.isspace():
                    self.saltar_espacios()
                    continue

                if self.caracter_actual.isdigit():
                    return self.numero()

                if self.caracter_actual.isalpha() or self.caracter_actual == '_':
                    return self.identificador()

                if self.caracter_actual == '+':
                    self.avanzar()
                    return ('SUMA', '+')

                if self.caracter_actual == '-':
                    self.avanzar()
                    return ('RESTA', '-')
                
                # Manejar números negativos
                if (self.caracter_actual == '-' and 
                    self.posicion < len(self.texto_entrada)-1 and 
                    self.texto_entrada[self.posicion+1].isdigit()):
                    self.avanzar()  # Consume el '-'
                    num_token = self.numero()
                    return ('ENTERO', -num_token[1])  # Devuelve el número como negativo


                if self.caracter_actual == '*':
                    self.avanzar()
                    return ('MULT', '*')

                if self.caracter_actual == '/':
                    self.avanzar()
                    return ('DIV', '/')

                if self.caracter_actual == ':':
                    self.avanzar()
                    if self.caracter_actual == '=':
                        self.avanzar()
                        return ('ASIGNACION', ':=')
                    else:
                        self.error()

                if self.caracter_actual == ';':
                    self.avanzar()
                    return ('PUNTO_COMA', ';')
                
                if self.caracter_actual == '<':
                    self.avanzar()
                    if self.caracter_actual == '=':
                        self.avanzar()
                        return ('MENOR_IGUAL', '<=')
                    elif self.caracter_actual == '>':
                        self.avanzar()
                        return ('DIFERENTE', '<>')
                    else:
                        return ('MENOR', '<')
                
                if self.caracter_actual == '>':
                    self.avanzar()
                    if self.caracter_actual == '=':
                        self.avanzar()
                        return ('MAYOR_IGUAL', '>=')
                    else:
                        return ('MAYOR', '>')
                
                if self.caracter_actual == '=':
                    self.avanzar()
                    return ('IGUAL', '=')
                
                if self.caracter_actual == '.':
                    self.avanzar()
                    return ('PUNTO', '.')
                
                if self.caracter_actual == '{':
                    self.avanzar()
                    return ('LBRACE', '{')
                if self.caracter_actual == '}':
                    self.avanzar()
                    return ('RBRACE', '}')
                
                if self.caracter_actual == '(':
                    self.avanzar()
                    return ('PAREN_IZQ', '(')
                    
                if self.caracter_actual == ')':
                    self.avanzar()
                    return ('PAREN_DER', ')')
                
                # Manejar números negativos y flotantes
                if (self.caracter_actual == '-' and 
                    self.posicion < len(self.texto_entrada)-1 and 
                    (self.texto_entrada[self.posicion+1].isdigit() or self.texto_entrada[self.posicion+1] == '.')):
                    self.avanzar()  # Consume el '-'
                    num_token = self.numero()
                    if num_token[0] == 'ENTERO':
                        return ('ENTERO', -num_token[1])
                    else:
                        return ('FLOTANTE', -num_token[1])

                # Manejar números positivos
                if self.caracter_actual.isdigit() or self.caracter_actual == '.':
                    return self.numero()
                
                if self.caracter_actual == '"':
                    return self.cadena()
                
                # Agregar reconocimiento de booleanos
                if self.caracter_actual.lower() == 't' and self.texto_entrada[self.posicion:self.posicion+4].lower() == 'true':
                    self.posicion += 4
                    self.caracter_actual = self.texto_entrada[self.posicion] if self.posicion < len(self.texto_entrada) else None
                    return ('BOOLEANO', True)
                    
                if self.caracter_actual.lower() == 'f' and self.texto_entrada[self.posicion:self.posicion+5].lower() == 'false':
                    self.posicion += 5
                    self.caracter_actual = self.texto_entrada[self.posicion] if self.posicion < len(self.texto_entrada) else None
                    return ('BOOLEANO', False)

                
                # Manejo robusto de :=
                if self.caracter_actual == ':':
                    start_pos = self.posicion
                    self.avanzar()
                    
                    # Permitir espacios opcionales
                    while self.caracter_actual is not None and self.caracter_actual.isspace():
                        self.avanzar()
                    
                    if self.caracter_actual != '=':
                        # Mostrar línea exacta del error
                        line_start = self.texto_entrada.rfind('\n', 0, start_pos) + 1
                        line_end = self.texto_entrada.find('\n', start_pos)
                        if line_end == -1:
                            line_end = len(self.texto_entrada)
                        error_line = self.texto_entrada[line_start:line_end]
                        caret_pos = start_pos - line_start
                        raise SyntaxError(
                            f"Se esperaba ':=' (línea {self.get_line_number(start_pos)})\n"
                            f"{error_line}\n"
                            f"{' ' * caret_pos}^"
                        )
                    
                    self.avanzar()
                    return ('ASIGNACION', ':=')

        except Exception as e:
            raise SyntaxError(f"Error léxico: {str(e)}")

    def get_line_number(self, pos):
        return self.texto_entrada.count('\n', 0, pos) + 1
    
    def cadena(self):
        resultado = ''
        self.avanzar()  # Saltar la comilla inicial
        
        while self.caracter_actual is not None and self.caracter_actual != '"':
            # Manejar caracteres escapados
            if self.caracter_actual == '\\':
                self.avanzar()
                if self.caracter_actual == 'n':
                    resultado += '\n'
                elif self.caracter_actual == 't':
                    resultado += '\t'
                else:
                    resultado += self.caracter_actual
                self.avanzar()
            else:
                resultado += self.caracter_actual
                self.avanzar()
        
        if self.caracter_actual != '"':
            raise SyntaxError("Cadena sin cerrar")
        
        self.avanzar()  # Saltar la comilla final
        return ('CADENA', resultado)

    def tokenizar(self):
        tokens = []
        while True:
            token = self.obtener_siguiente_token()
            
            if token is None:
                break
                
            if token[0] in ('EOF', 'FIN_ARCHIVO'):
                break
                
            if token[0] == 'ERROR':
                print(f"Error léxico: {token[1]}")
                continue
                
            tokens.append(token)
            if self.debug:  # Solo mostrar tokens en modo debug
                print(f"Token reconocido: {token}")
            
        return tokens