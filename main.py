# Importação de bibliotecas
import sys
from antlr4 import *
from LALexer import LALexer
from LAParser import LAParser
from LASemantico import LASemantico
from Analisador import Analisador

sys.setrecursionlimit(10000)


# Leitura dos nomes e abertura dos arquivos
input_file_name = sys.argv[1]
output_file_name = sys.argv[2]
input_stream = FileStream(input_file_name, encoding="utf-8")
output = open(output_file_name, "w")

# Criando o analisador léxico
lexer = LALexer(input_stream)

# Criando o fluxo de tokens
stream = CommonTokenStream(lexer)

# Criando o analisador sintático
parser = LAParser(stream)

arvore = parser.programa()
listener = LASemantico()
# parser.addParseListener(listener)

# parser.programa()
listener.visitPrograma(arvore)

# Escrita dos erros na saida
for error in Analisador.erros:
    output.write(error + "\n")
    print(error)
output.write("Fim da compilacao" + "\n")
output.close()
