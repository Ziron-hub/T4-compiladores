from enum import Enum


class TabelaDeSimbolos:
    class TipoLA(Enum):
        INTEIRO = 1
        REAL = 2
        LITERAL = 3
        LOGICO = 4
        INVALIDO = 5
        REGISTRADOR = 6
        VOID = 7

    class Estrutura(Enum):
        VARIAVEL = 1
        CONSTANTE = 2
        PROCEDIMENTO = 3
        FUNCAO = 4
        TIPO = 5

    class EntradaTabelaDeSimbolos:
        def __init__(self, nome, tipo, estrutura):
            self.nome = nome
            self.tipo = tipo
            self.estrutura = estrutura

    def __init__(self, tipo):
        self.tabelaDeSimbolos = {}
        self.tabelaTipo = {}
        self.tipo = tipo

    def adicionar_tabela_simbolos(self, nome: str, tipo: TipoLA, estrutura: Estrutura):
        etds = TabelaDeSimbolos.EntradaTabelaDeSimbolos(nome, tipo, estrutura)
        self.tabelaDeSimbolos[nome] = etds

    def adicionar_entrada_tabela_simbolos(self, entradaTabelaSimbolos: EntradaTabelaDeSimbolos):
        self.tabelaDeSimbolos[entradaTabelaSimbolos.nome] = entradaTabelaSimbolos

    def adicionar_tipo_nome(self, tipoNome: str, entradaTabelaSimbolos: EntradaTabelaDeSimbolos):

        if tipoNome in self.tabelaTipo:
            self.tabelaTipo.get(tipoNome).append(entradaTabelaSimbolos)
        else:
            list = []
            list.append(entradaTabelaSimbolos)
            self.tabelaTipo[tipoNome] = list

    def contem(self, nome: str):
        return nome in self.tabelaDeSimbolos

    def verificar(self, nome: str):
        return self.tabelaDeSimbolos.get(nome).tipo
    
    def verificar_tipo(self, nome: str):
        return self.tabelaTipo.get(nome) 


class Escopo:
    def __init__(self, tipo: TabelaDeSimbolos.TipoLA):
        self.pilhaDeTabelas = []
        self.criar_novo_escopo(tipo)

    def criar_novo_escopo(self, tipo: TabelaDeSimbolos.TipoLA):
        self.pilhaDeTabelas.append(TabelaDeSimbolos(tipo))

    def obter_escopo_atual(self):
        return self.pilhaDeTabelas[-1]
    
    def obter_pilha(self):
        return self.pilhaDeTabelas

    def abandonar_escopo(self):
        self.pilhaDeTabelas.pop()

    def identificador_existe(self, nome: str):
        for tabela in self.pilhaDeTabelas:
            if not tabela.contem(nome):
                return True
        return False

