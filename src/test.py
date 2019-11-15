from semanticanalyzer import SemanticAnalyzer
import sys

if __name__ == "__main__":
  if len(sys.argv) > 1:
    file_name = sys.argv[1]
  else:
    file_name = '../data/test2.txt'
    print("Se puede introducir el nombre del archivo como parámetro.")
  print("Archivo seleccionado: ", file_name)

  sa = SemanticAnalyzer()
  try:
    sa.loadfile(file_name)
    try:
      v = sa.file.split('\n')
      print('──┐')
      for i,line in enumerate(v):
        print(('0' if i+1 < 10 else '') + str(i+1) + "│" + line)
      print('──┘')
      result = sa.parse()
      print("No ha habido ningún error." if result == "" else result)
    except:
      print("Archivo invalido.")
  except:
    print("Nombre de archivo invalido")

