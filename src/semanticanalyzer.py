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
    self.types = {'void', 'int', 'float', 'string'}
    self.reserved = {'if', 'while'}

  @property
  def file(self):
    return self._file

  @file.setter
  def file(self, value):
    self._file = value

  @property
  def table(self):
    return self._table

  @table.setter
  def table(self, value):
    self._table = value

  def loadfile(self, filename):
    with open(filename, 'r') as file:
      self.file = file.read()
      self.file = re.sub(r'[\n\t]+', '', self.file) # Esto quita los carácteres '\n' y '\t'.

  def getErrors(self):
    def parse(owner, string, line = 0):
      first = re.search(r'^[A-Za-z]+', string)
      if first is None:
        return ""
      first = first.group(0)
      if first in self.types:
        second = re.search(r'[A-Za-z]+ ([A-Za-z]+)', string).group(1)
        if second in self.table:
          return f"\nError - Línea {line}: '{second}' ya está declarado."
        self.table.insert(second, first)
      else:
        if first == 'return':
          second = re.search(r'return ([A-Za-z]+)', string).group(1)
          if second not in self.table:
            return f"\nError - Línea {line}: '{first}' no está declarado."
          if owner is None:
            return f"\nError - Línea {line}: retorno a nivel global."
          if self.table[second].type != owner.type:
            return (f"\nError - Línea {line}: valor de retorno no coincide con"
                     " la declaración de '{owner.name}'.")
        elif first not in self.table:
          return f"\nError - Línea {line}: '{first}' no está declarado."
      return ""

    result = ""
    source = self.file
    owner = None

    while(len(source) > 0):
      # Paso 1. Verificar si es más largo el string hasta el siguiente ';' o
      # hasta el siguiente '{'.
      extracted_string_1 = source.split(';')[0]
      extracted_string_1 = extracted_string_1.strip()
      extracted_string_2 = source.split('{')[0]
      extracted_string_2 = extracted_string_2.strip()
      
      if len(extracted_string_1) < len(extracted_string_2):
        source = source[len(extracted_string_1) + 1:]
        result += parse(owner, extracted_string_1)
      else:
        source = source[len(extracted_string_2) + 1:]
        result += parse(owner, extracted_string_2)

    self.table = SymbolTable()
    return re.sub(r'^\n', '', result)

