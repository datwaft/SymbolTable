# semanticanalyzer.py
# Integrantes: David Guevara y Mario Arguello
# Descripción: contiene un analizador semántico que agarra como input un string
#              que contiene código de c++ básico y analiza sus errores de scope
#              y de valor de retorno.


import re
from symboltable import SymbolTable

class SemanticAnalyzer:
  """
  Esta clase es un analizador semántico que se encarga de analizar el string de
  entrada para dar los errores que el mismo contiene.

  Atributos:
  - file:       contiene el archivo a analizar como un solo string.

  - table:      contiene la tabla de símbolos para poder analizar los símbolos
                declarados.

  - scopestack: es una lista que funciona como pila para almacenar las funciones
                dueñas de los scopes anteriores.

  - scope:      contiene la función dueña del scope actual, si es None el scope
                es global.

  - types:      contiene cada uno de los tipos validos.

  - reserved:   contiene cada una de las palabras reservadas.

  - err:        diccionario que contiene todos los errores con el proposito de
                usar .format() con ellos.

  - expr:       diccionario que contiene cada una de las expresiones regulares
                compiladas para facilidad de uso. 
  """
  def __init__(self, string = None):
    """
    Inicializa cada una de las variables y agarra un string de archivo.
    """
    self.file = string
    self.table = SymbolTable()
    self.scopestack = []
    self.scope = None
    self.types = {'void', 'int', 'float', 'string'}
    self.reserved = {'if', 'while'}
    self.err = dict()
    self.generate_errors()
    self.expr = dict()
    self.generate_expressions()

  def generate_errors(self):
    """
    Cada uno de los erroes preparados para ser usados.
    """
    self.err['ndcl'] = "\nError - Línea {0}: '{1}' no está declarado."
    self.err['dcl'] = "\nError - Línea {0}: '{1}' ya está declarado."
    self.err['ret'] = ("\nError - Línea {0}: valor de retorno no coincide con la"
                       " declaración de '{1}'.")
    self.err['gret'] = "\nError - Línea {0}: retorno a nivel global."

  def generate_expressions(self):
    """
    Cada una de las expresiones precompiladas preparadas para ser usadas.
    """
    # Hace match con expresiones que sea palabras que no estén entre '"'.
    self.expr['var'] = re.compile(r'[A-Za-z]+(?=(?:[^"]*"[^"]*")*[^"]*\Z)')
    # Hace match von una palabra al inicio.
    self.expr['beg'] = re.compile(r'^[A-Za-z]+')
    # Hace match con dos palabras al inicio, la segunda palabra se guarda en el
    # grupo 1.
    self.expr['2nd'] = re.compile(r'^[A-Za-z]+ ([A-Za-z]+)')
    # Hace match con n carácteres que puede estar separados por un espacio con
    # unos paréntesis.
    # El grupo 1 son esos n carácteres y el grupo 2 es lo que está dentro de los
    # paréntesis.
    self.expr['()'] = re.compile(r'(.+) ?\((.+)\)')
    # Hace match con n carácteres de new line.
    self.expr['nl'] = re.compile(r'\n+')

  def loadfile(self, filename):
    """
    Abre el archivo e intenta abrirlo, el atributo file pasa a ser el string del
    archivo.
    """
    with open(filename, 'r') as file:
      self.file = file.read()

  def setscope(self, scope):
    """
    Cambia el dueño del scope actual guardando el anterior en la pila.
    """
    self.scopestack.append(self.scope)
    self.scope = scope

  def retscope(self):
    """
    Se devuelve al dueño anterior que había sido guardado en la pila.
    """
    if len(self.scopestack) == 0:
      self.scope = None
    else:
      self.scope = self.scopestack.pop()

  def parsestatement(self, string, line):
    """
    Parsea una línea.
    e.g. int x = 0;
         string s = "hola"
         int x, int y, int z
    """
    if string is None:
      return ""
  
    # Extrae en un vector todas las variables y tipos.
    v = self.expr['var'].findall(string)
    
    result = "" # Guarda los errores que se van a devolver.
    prev_type = None # Se utiliza para ver si el elemento anterior era un tipo.
    for e in v: 
      if prev_type is not None:
        if e in self.table:
          if prev_type == 'return':
            if self.scope is None:
              result += self.err['gret'].format(line)
            elif self.scope.type != self.table[e].type:
              result += self.err['ret'].format(line, self.scope.name)
          else:
            result += self.err['dcl'].format(line, e)
        else:
          if prev_type == 'return':
            result += self.err['ndcl'].format(line, e)
          else:
            self.table.insert(e, prev_type)
        prev_type = None
      else:
        if e in self.types or e == 'return':
          prev_type = e
        elif e not in self.table:
          result += self.err['ndcl'].format(line, e)
    return result

  def parsefunction(self, string, line):
    """
    Parsea una función.
    e.g. void funcion(int x, int y, int z)
    """
    result = ""
    # Separa las dos partes: 'void funcion' & '(int x, int y, int z)'.
    s1, s2 = self.expr['()'].match(string).groups()
    st = self.expr['beg'].match(string).group(0)
    if st in self.types:
      sn = self.expr['2nd'].match(string).group(1)
      if sn in self.table:
        result += self.err['dcl'].format(line, sn)
      else:
        self.table.insert(sn, st)
        self.setscope(self.table[sn])
    elif s1 not in self.reserved:
      result += self.parsestatement(s1, line)
    else:
      self.setscope(self.scope)
    
    # Crea el nuevo scope antes para guardar los parámetros ahí.
    self.table = self.table.newscope()

    result += self.parsestatement(s2, line)
    return result

  def parse(self):
    """
    Parsea un archivo entero hasta el final y devuelve los errores encontrados.
    """
    result = ""
    source = self.file
    source = re.sub(r'\t+', '', source) # Esto quita los carácteres \t'.
    source = re.sub(r' {2,}', ' ', source) # Elimina el exceso de espacios.

    line = 1

    while(len(source) > 0):
      # Esto se usa para ver cuáles elementos existen y cuál de los existentes
      # es el más cercano.
      len1 = -1
      len2 = -1
      len3 = -1
      
      v = []

      # Si existe lo añade al vector de elementos existentes.
      if ';' in source:
        len1 = source.index(';')
        v += [len1]
      if '{' in source:
        len2 = source.index('{')
        v += [len2]
      if '}' in source:
        len3 = source.index('}')
        v += [len3]
      
      this = min(v)
    
      #  Dice el número de línea según cuántos '\n' se han econtrado.
      if '\n' in source[:this]:
        line += source[:this].count('\n')

      if this == len1: # Si el más cercano fue un ';'.
        result += self.parsestatement(self.expr['nl'].sub('',
          source[:this].strip()), line)
      elif this == len2: # Si el más cercano fue un '{'.
        result += self.parsefunction(self.expr['nl'].sub('',
          source[:this].strip()), line)
      else: # Si el más cercano fue un '}'.
        self.retscope()
        self.table = self.table.getfather()
        
      # Elimina lo que se acaba de parsear junto con el carácter delimitador.
      source = source[this + 1:]

    # Reinicia el scope.
    self.table = SymbolTable()
    self.scope = None
    # Para eliminar las línea repetidas.
    l = list(dict.fromkeys(re.sub(r'^\n', '', result).split('\n')))
    res = ''.join(s + '\n' for s in l)
    return re.sub(r'\n$', '', res)

