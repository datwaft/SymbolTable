# symboltable.py
# Integrantes: David Guevara y Mario Arguello
# Descripción: contiene una implementación de una tabla de símbolos.

class Entry:
  """
  Una entrada de la tabla de símbolos.

  Atributos:
  - name: nombre de la entrada.
  - type: tipo de la entrada
  """
  def __init__(self, symbolname, symboltype):
    """
    Inicializa la entrada de la tabla.
    """
    self.name = symbolname
    self.type = symboltype

  def __str__(self):
    """
    Utilizado para imprimir la entrada de la tabla en pantalla.
    """
    return f"<{self.name}, {self.type}>"

  def __repr__(self):
    """
    Utilizado para imprimir la entrada de la tabla en pantalla.
    """
    return str(self)

class SymbolTable:
  """
  Una tabla de símbolos.

  Sirve para almacenar entradas de la tabla de símbolos.

  Tiene un padre para que se pueda derivar una tabla de símbolos de otra y que
  la nueva igual tenga acceso a las entradas de la anterior, esto permite crear
  scopes.

  Atributos:
  - _table: un diccionario usado para almacenar cada entrada de la tabla actual.
  - _father: la tabla de símbolos anterior a la actual.
  """
  def __init__(self):
    """
    Inicializa la tabla de simbolos.
    Si la tabla fue creada por este método, no va a tener padre.
    """
    self._table = dict()
    self._father = None

  def symbols(self):
    """
    Devuelve una lista de entadas de la tabla, tanto las de la tabla actual como
    las de las anteriores a esta.
    Primero van las entradas del padre y luego las nuevas.
    """
    l = list(self._table.values())
    if self._father is not None:
      l = self._father.symbols() + l
    return l

  def __iter__(self):
    """
    Permite hacer list(SymbolTable).
    """
    for i in self.symbols():
      yield i

  def insert(self, symbol, symboltype):
    """
    Inserta un elemento con su tipo en la tabla.
    """
    if symbol not in self:
      self._table[symbol] = Entry(symbol, symboltype)

  def delete(self, symbol):
    """
    Si el elemento está presente, lo elimina de la tabla.
    El elemento puede estar presente en la tabla actual o en el padre que igual
    lo elimina.
    """
    if symbol in self:
      if symbol in self._table:
        self._table.pop(symbol)
      else:
        self._father.delete(symbol)

  def lookup(self, symbol):
    """
    Devuelve un elemento de la tabla.
    Se fija primero si el elemento está, y una vez sabe que está se fija en el
    padre de ser posible, y luego en la actual.
    """
    if symbol in self:
      if self._father is not None:
        aux = self._father.lookup(symbol)
        if aux is None:
          return self._table[symbol]
        else:
          return aux
      return self._table[symbol]
    return None

  def __getitem__(self, key):
    """
    Sobrecarga para poder hacer SymbolTable['EntryName'].
    """
    return self.lookup(key)

  def __contains__(self, key):
    """
    Dice si un elemento está presente en la tabla, puede estar en el padre o en
    la actual.
    """
    if self._father is not None:
      return key in self._table or key in self._father
    return key in self._table

  def newscope(self):
    """
    Crea un nuevo 'scope'.
    Devuelve una nueva tabla de símbolos con la actual como anterior.
    """
    aux = SymbolTable()
    aux._father = self
    return aux

  def getfather(self):
    """
    Devuelve el 'scope' anterior, sirve para eliminar scopes.
    """
    return self._father

