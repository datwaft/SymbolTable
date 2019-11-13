import re
from symboltable import SymbolTable

class SemanticAnalyzer:
  """
  Esta clase es un analizador semántico que se encarga de analizar el string de
  entrada para dar los errores que el mismo contiene.
  """
  def __init__(self, string = None):
    self.file = string
    self.table = SymbolTable()
    self.scope = None
    self.types = {'void', 'int', 'float', 'string'}
    self.reserved = {'if', 'while'}
    self.err = dict()
    self.generate_errors()
    self.expr = dict()
    self.generate_expressions()

  def generate_errors(self):
    self.err['ndcl'] = "\nError - Línea {0}: '{1}' no está declarado."
    self.err['dcl'] = "\nError - Línea {0}: '{1}' ya está declarado."
    self.err['ret'] = ("\nError - Línea {0}: valor de retorno no coincide con la"
                       " declaración de '{1}'.")
    self.err['gret'] = "\nError - Línea {0}: retorno a nivel global."

  def generate_expressions(self):
    self.expr['var'] = re.compile(r'[A-Za-z]+(?=(?:[^"]*"[^"]*")*[^"]*\Z)')
    self.expr['beg'] = re.compile(r'^[A-Za-z]+')
    self.expr['2nd'] = re.compile(r'^[A-Za-z]+ ([A-Za-z]+)')
    self.expr['()'] = re.compile(r'(.+) ?\((.+)\)')

  def loadfile(self, filename):
    with open(filename, 'r') as file:
      self.file = file.read()
      self.file = re.sub(r'[\n\t]+', '', self.file) # Esto quita los carácteres '\n' y '\t'.

  def parsestatement(self, string, line):
    if string is None:
      return ""

    v = self.expr['var'].findall(string)
    
    result = ""
    prev_type = None
    for e in v:
      if prev_type is not None:
        if e in self.table:
          if prev_type == 'return':
            if self.scope is None:
              result += self.err['gret'].format(line)
            elif self.scope.type != self.table[e].type:
              result += self.err['ret'].format(line, e)
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
    result = ""
    s1, s2 = self.expr['()'].match(string).groups()
    st = self.expr['beg'].match(string).group(0)
    if st in self.types:
      sn = self.expr['2nd'].match(string).group(1)
      if sn in self.table:
        result += self.err['dcl'].format(line, sn)
      else:
        self.table.insert(sn, st)
        self.scope = self.table[sn]
    elif s1 not in self.reserved:
      result += self.parsestatement(s1, line)

    result += self.parsestatement(s2, line)
    return result

  def parse(self):
    result = ""
    source = self.file

    while(len(source) > 0):
      # Paso 1. Verificar si es más largo el string hasta el siguiente ';' o
      # hasta el siguiente '{'.
      extracted_string_1 = source.split(';')[0]
      extracted_string_1 = extracted_string_1.strip()
      extracted_string_2 = source.split('{')[0]
      extracted_string_2 = extracted_string_2.strip()
      
      if len(extracted_string_1) < len(extracted_string_2):
        source = source[len(extracted_string_1) + 1:]
        result += self.parsestatement(extracted_string_1, 'x')
      else:
        source = source[len(extracted_string_2) + 1:]
        result += self.parsefunction(extracted_string_2, 'x')

    self.table = SymbolTable()
    return re.sub(r'^\n', '', result)

if __name__ == "__main__":
  sa = SemanticAnalyzer()
  sa.loadfile('../data/test2.txt')
  print(sa.file)
  print(sa.parse())
