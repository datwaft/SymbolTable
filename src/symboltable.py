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
  """
  def __init__(self):
    """
    Inicializa la tabla de simbolos.
    """
    self._table = dict()
    self._father = None
  
  def symbols(self):
    l = list(self._table.values())
    if self._father is not None:
      l = self._father.symbols() + l
    return l

  def __iter__(self):
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
    """
    if symbol in self:
      if symbol in self._table:
        self._table.pop(symbol)
      else:
        self._father.delete(symbol)

  def lookup(self, symbol):
    """
    Devuelve un elemento de la tabla.
    """
    if symbol in self:
      if self._father is not None:
        aux = self._father.lookup(symbol)
        if aux is None:
          return self._table[symbol]
      return self._table[symbol]
    return None

  def __getitem__(self, key):
    return self.lookup(key)
  
  def __contains__(self, key):
    """
    Dice si un elemento está presente en la tabla.
    """
    if self._father is not None:
      return key in self._table or key in self._father
    return key in self._table

  def newscope(self):
    """
    Crea un nuevo 'scope'.
    """
    aux = SymbolTable()
    aux._father = self
    return aux

  def getfather(self):
    """
    Devuelve el 'scope' anterior, sirve para eliminar scopes.
    """
    return self._father

