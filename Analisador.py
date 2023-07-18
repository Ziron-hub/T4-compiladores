from Estruturas import TabelaDeSimbolos, Escopo
from LAParser import LAParser

# Analisador semântico
class Analisador:

    erros = []

    # Controle dos erros
    def adicionar_erro_semantico(token, mensagem):

        linha = token.line
        Analisador.erros.append(f"Linha {linha}: {mensagem}")

    # Verificacao de fator logico
    def verificar_tipo_fator_logico(escopos, contexto):

        return Analisador.verificar_tipo_parcela_logica(escopos, contexto.parcela_logica())
    # Verificacao de parcela logica
    def verificar_tipo_parcela_logica(escopos, contexto):

        functionReturn = None

        if contexto.exp_relacional() is not None:
            functionReturn = Analisador.verificar_tipo_exp_relacional(escopos, contexto.exp_relacional())
        else:
            functionReturn = TabelaDeSimbolos.TipoLA.LOGICO

        return functionReturn
    # Verificacao de parcela nao unaria
    def verificar_tipo_parcela_nao_unario(escopos, contexto):
        
        if contexto.identificador() is not None:
            return Analisador.verificar_tipo_identificador(escopos, contexto.identificador())

        return TabelaDeSimbolos.TipoLA.LITERAL
    # Verificacao de parcela unaria
    def verificar_tipo_parcela_unario(escopos, contexto):
        
        if contexto.NUM_INT() is not None:
            return TabelaDeSimbolos.TipoLA.INTEIRO
        if contexto.NUM_REAL() is not None:
            return TabelaDeSimbolos.TipoLA.REAL
        if contexto.identificador() is not None:
            return Analisador.verificar_tipo_identificador(escopos, contexto.identificador())
        if contexto.IDENT() is not None:
            return Analisador.verificar_tipo_nome_var(escopos, contexto.IDENT().getText())

        else:
            functionReturn = None
            for expressao in contexto.expressao():
                aux = Analisador.verificar_tipo_expressao(escopos, expressao)
                functionReturn = aux
            
            return functionReturn
    # Verificacao de termo logico
    def verificar_tipo_termo_logico(escopos, contexto):

        functionReturn = None

        for fatorLogico in contexto.fator_logico():
            aux = Analisador.verificar_tipo_fator_logico(escopos, fatorLogico)
            functionReturn = aux

        return functionReturn
    # Verificacao de expressao relacional
    def verificar_tipo_exp_relacional(escopos, contexto):

        functionReturn = None

        if contexto.op_relacional() is not None:
            for expAritmetica in contexto.exp_aritmetica():
                aux = Analisador.verificar_tipo_exp_aritmetica(escopos, expAritmetica)
                functionReturn = aux

            if functionReturn != TabelaDeSimbolos.TipoLA.INVALIDO:
                functionReturn = TabelaDeSimbolos.TipoLA.LOGICO

        else:
            functionReturn = Analisador.verificar_tipo_exp_aritmetica(escopos, contexto.exp_aritmetica(0))

        return functionReturn
    # Verificacao de nome de variavel
    def verificar_tipo_nome_var(escopos, nomeVar: str):
        tipo = TabelaDeSimbolos.TipoLA.INVALIDO

        for tabela in escopos.obter_pilha():
            if tabela.contem(nomeVar):
                return tabela.verificar(nomeVar)
            
        return tipo
    # Verificacao de expressao aritmetica
    def verificar_tipo_exp_aritmetica(escopos, contexto):

        functionReturn = None

        for termo in contexto.termo():
            aux = Analisador.verificar_tipo_termo(escopos, termo)
            functionReturn = aux

        return functionReturn
    # Verificacao de termos
    def verificar_tipo_termo(escopos, contexto):

        functionReturn = None

        for fator in contexto.fator():
            aux = Analisador.verificar_tipo_fator(escopos, fator)
            functionReturn = aux

        return functionReturn
    # Verificacao de fator
    def verificar_tipo_fator(escopos, contexto):

        functionReturn = None

        for parcela in contexto.parcela():
            aux = Analisador.verificar_tipo_parcela(escopos, parcela)
            functionReturn = aux

        return functionReturn
    # Verificao de expressao
    def verificar_tipo_expressao(escopos, ctx):

        functionReturn = None

        for termoLogico in ctx.termo_logico():
            aux = Analisador.verificar_tipo_termo_logico(escopos, termoLogico)
            functionReturn = aux

        return functionReturn
    # Verificar parcela
    def verificar_tipo_parcela(escopos, contexto):

        functionReturn = TabelaDeSimbolos.TipoLA.INVALIDO

        if contexto.parcela_nao_unario() is not None:
            functionReturn = Analisador.verificar_tipo_parcela_nao_unario(escopos, contexto.parcela_nao_unario())
        else:
            functionReturn = Analisador.verificar_tipo_parcela_unario(escopos, contexto.parcela_unario())
        return functionReturn
    # Verificacao de identificador
    def verificar_tipo_identificador(escopos, contexto):

        nomeVar = ''
        functionReturn = TabelaDeSimbolos.TipoLA.INVALIDO
        for i in range(len(contexto.IDENT())):
            nomeVar += contexto.IDENT(i).getText()

            if i != len(contexto.IDENT()) - 1:
                nomeVar += '.'

        for tabela in escopos.obter_pilha():
            if tabela.contem(nomeVar):
                functionReturn = Analisador.verificar_tipo_nome_var(escopos, nomeVar)

        return functionReturn

    # Retorna o tipo
    def get_tipo(valor: str):
        tipo = None
        if valor == 'literal':
            tipo = TabelaDeSimbolos.TipoLA.LITERAL
        elif valor == 'inteiro':
            tipo = TabelaDeSimbolos.TipoLA.INTEIRO
        elif valor == 'real':
            tipo = TabelaDeSimbolos.TipoLA.REAL
        elif valor == 'logico':
            tipo = TabelaDeSimbolos.TipoLA.LOGICO
        return tipo