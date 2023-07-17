from LAParser import LAParser
from LAVisitor import LAVisitor
from Estruturas import TabelaDeSimbolos, Escopo
from Analisador import Analisador
from typing import List

class LASemantico(LAVisitor):
    def __init__(self):
        self.escopos = Escopo(TabelaDeSimbolos.TipoLA.VOID)

    def visitPrograma(self, contexto):
        return super().visitPrograma(contexto)

    def visitDeclaracao_constante(self, contexto):
        escopoAtual = self.escopos.obter_escopo_atual()

        if escopoAtual.contem(contexto.IDENT().getText()):
            Analisador.adicionar_erro_semantico(
                token=contexto.start,
                mensagem=f'constante {contexto.IDENT().getText()} ja declarado anteriormente'
            )
        else:
            tipo = TabelaDeSimbolos.TipoLA.INTEIRO
            aux = Analisador.get_tipo(contexto.tipo_basico().getText())
            if aux is not None:
                tipo = aux

            escopoAtual.adicionar_tabela_simbolos(
                contexto.IDENT().getText(), tipo, TabelaDeSimbolos.Estrutura.CONSTANTE
            )

        return super().visitDeclaracao_constante(contexto)

    def visitParcela_unario(self, ctx):
        escopoAtual = self.escopos.obter_escopo_atual()
        if ctx.IDENT() is not None:
            nome = ctx.IDENT().getText()
            if escopoAtual.contem(nome):
                params = escopoAtual.verificar_tipo(nome)
                erro = False
                if len(params) != len(ctx.expressao()):
                    erro = True
                else:
                    for i in range(len(params)):
                        if params[i].tipo != Analisador.verificar_tipo_expressao(escopos=self.escopos, ctx=ctx.expressao()[i]):
                            erro = True
                if erro:
                    Analisador.adicionar_erro_semantico(ctx.start, f"incompatibilidade de parametros na chamada de {nome}")
        
        return super().visitParcela_unario(ctx)


    def visitDeclaracao_variavel(self, contexto):
        escopoAtual = self.escopos.obter_escopo_atual()

        for identificador in contexto.variavel().identificador():
            nomeId = '.'.join(ident.getText() for ident in identificador.IDENT())
            
            if escopoAtual.contem(nomeId):
                Analisador.adicionar_erro_semantico(identificador.start,
                                                    f'identificador {nomeId} ja declarado anteriormente')
            else:
                tipo = Analisador.get_tipo(contexto.variavel().tipo().getText())
                if tipo is not None:
                    escopoAtual.adicionar_tabela_simbolos(nomeId, tipo, TabelaDeSimbolos.Estrutura.VARIAVEL)
                else:
                    identTipo = contexto.variavel().tipo().tipo_estendido().tipo_basico_ident().IDENT() if (
                            contexto.variavel().tipo() is not None
                            and contexto.variavel().tipo().tipo_estendido() is not None
                            and contexto.variavel().tipo().tipo_estendido().tipo_basico_ident() is not None
                            and contexto.variavel().tipo().tipo_estendido().tipo_basico_ident().IDENT() is not None
                    ) else None
                    if identTipo is not None:
                        registros = None
                        for tabela in self.escopos.obter_pilha():
                            if tabela.contem(identTipo.getText()):
                                registros = tabela.verificar_tipo(identTipo.getText())
                        if escopoAtual.contem(nomeId):
                            Analisador.adicionar_erro_semantico(identificador.start,
                                                                f"identificador {nomeId} ja declarado anteriormente")
                        else:
                            escopoAtual.adicionar_tabela_simbolos(nomeId, TabelaDeSimbolos.TipoLA.REGISTRADOR,
                                                                TabelaDeSimbolos.Estrutura.VARIAVEL)
                            if registros is not None:
                                for registro in registros:
                                    escopoAtual.adicionar_tabela_simbolos(
                                        nomeId + '.' + registro.nome, registro.tipo, TabelaDeSimbolos.Estrutura.VARIAVEL
                                    )
                    elif contexto.variavel().tipo().registro() is not None:
                        registros: List[TabelaDeSimbolos.EntradaTabelaDeSimbolos] = []
                        for variavel in contexto.variavel().tipo().registro().variavel():
                            tipoRegistros = Analisador.get_tipo(variavel.tipo().getText())
                            for ident in variavel.identificador():
                                entrada = TabelaDeSimbolos.EntradaTabelaDeSimbolos(ident.getText(), tipoRegistros,
                                                                                    TabelaDeSimbolos.Estrutura.VARIAVEL)
                                escopoAtual.adicionar_entrada_tabela_simbolos(entrada)
                                registros.append(entrada)
                        escopoAtual.adicionar_tabela_simbolos(nomeId, TabelaDeSimbolos.TipoLA.REGISTRADOR,
                                                            TabelaDeSimbolos.Estrutura.VARIAVEL)

                        for registro in registros:
                            nomeVar = nomeId + '.' + registro.nome
                            if escopoAtual.contem(nomeVar):
                                Analisador.adicionar_erro_semantico(identificador.start,
                                                                    f"identificador {nomeVar} ja declarado anteriormente")
                            else:
                                escopoAtual.adicionar_entrada_tabela_simbolos(registro)
                                escopoAtual.adicionar_tabela_simbolos(nomeVar, registro.tipo,
                                                                    TabelaDeSimbolos.Estrutura.VARIAVEL)
                    else:
                        escopoAtual.adicionar_tabela_simbolos(identificador.getText(), TabelaDeSimbolos.TipoLA.INTEIRO,
                                                            TabelaDeSimbolos.Estrutura.VARIAVEL)

        return super().visitDeclaracao_variavel(contexto)
    
    def visitDeclaracao_tipo(self, contexto):
        escopoAtual = self.escopos.obter_escopo_atual()
        identificador = contexto.IDENT().getText()

        if escopoAtual.contem(identificador):
            Analisador.adicionar_erro_semantico(
                token=contexto.start,
                mensagem=f'tipo {identificador} declarado duas vezes no mesmo escopo'
            )
        else:
            tipo = Analisador.get_tipo(contexto.tipo().getText())

            if tipo is not None:
                escopoAtual.adicionar_tabela_simbolos(identificador, tipo, TabelaDeSimbolos.Estrutura.TIPO)
            elif contexto.tipo().registro() is not None:
                varRegistros = []
                for variavel in contexto.tipo().registro().variavel():
                    tipoRegistrador = Analisador.get_tipo(variavel.tipo().getText())
                    for ident in variavel.identificador():
                        entrada = TabelaDeSimbolos.EntradaTabelaDeSimbolos(ident.getText(), tipoRegistrador, TabelaDeSimbolos.Estrutura.TIPO)
                        escopoAtual.adicionar_entrada_tabela_simbolos(entrada)
                        varRegistros.append(entrada)

                if escopoAtual.contem(identificador):
                    Analisador.adicionar_erro_semantico(
                        token=contexto.start,
                        mensagem=f'identificador {identificador} já declarado anteriormente'
                    )
                else:
                    escopoAtual.adicionar_tabela_simbolos(identificador, TabelaDeSimbolos.TipoLA.REGISTRADOR, TabelaDeSimbolos.Estrutura.TIPO)

                for registro in varRegistros:
                    nomeVar = identificador + '.' + registro.nome
                    if escopoAtual.contem(nomeVar):
                        Analisador.adicionar_erro_semantico(
                            token=contexto.start,
                            mensagem=f'identificador {nomeVar} já declarado anteriormente'
                        )
                    else:
                        escopoAtual.adicionar_entrada_tabela_simbolos(registro)
                        escopoAtual.adicionar_tipo_nome(identificador, registro)

            escopoAtual.adicionar_tabela_simbolos(identificador, tipo, TabelaDeSimbolos.Estrutura.TIPO)

        return super().visitDeclaracao_tipo(contexto)

    def visitDeclaracao_global(self, contexto):
        escopoAtual = self.escopos.obter_escopo_atual()

        if escopoAtual.contem(contexto.IDENT().getText()):
            Analisador.adicionar_erro_semantico(contexto.start, f'{contexto.IDENT().getText()} ja declarado anteriormente')
            functionReturn = super().visitDeclaracao_global(contexto)
        else:
            tipoRetornoFuncao = TabelaDeSimbolos.TipoLA.VOID
            if contexto.getText().startswith("funcao"):
                tipoRetornoFuncao = Analisador.get_tipo(contexto.tipo_estendido().getText())
                estrutura = TabelaDeSimbolos.Estrutura.FUNCAO
            else:
                estrutura = TabelaDeSimbolos.Estrutura.PROCEDIMENTO

            escopoAtual.adicionar_tabela_simbolos(contexto.IDENT().getText(), tipoRetornoFuncao, estrutura)

            self.escopos.criar_novo_escopo(tipoRetornoFuncao)
            escopoAntigo = escopoAtual
            escopoAtual = self.escopos.obter_escopo_atual()

            if contexto.parametros() is not None:
                for param in contexto.parametros().parametro():
                    for id in param.identificador():
                        nomeId = '.'.join(ident.getText() for ident in id.IDENT())

                        if escopoAtual.contem(nomeId):
                            Analisador.adicionar_erro_semantico(id.start, f'identificador {nomeId} ja declarado anteriormente')
                        else:
                            tipo = Analisador.get_tipo(param.tipo_estendido().getText())
                            if tipo is not None:
                                entradaTabela = TabelaDeSimbolos.EntradaTabelaDeSimbolos(nomeId, tipo, TabelaDeSimbolos.Estrutura.VARIAVEL)
                                escopoAtual.adicionar_entrada_tabela_simbolos(entradaTabela)
                                escopoAntigo.adicionar_tipo_nome(contexto.IDENT().getText(), entradaTabela)
                            else:
                                identTipo = param.tipo_estendido().tipo_basico_ident().IDENT() if (
                                        param.tipo_estendido().tipo_basico_ident() is not None
                                        and param.tipo_estendido().tipo_basico_ident().IDENT() is not None
                                ) else None
                                if identTipo is not None:
                                    regVars = None
                                    for tabela in self.escopos.obter_pilha():
                                        if tabela.contem(identTipo.getText()):
                                            regVars = tabela.verificar_tipo(identTipo.getText())
                                    if escopoAtual.contem(nomeId):
                                        Analisador.adicionar_erro_semantico(id.start, f"identificador {nomeId} ja declarado anteriormente")
                                    else:
                                        entradaTabela = TabelaDeSimbolos.EntradaTabelaDeSimbolos(nomeId, TabelaDeSimbolos.TipoLA.REGISTRADOR, TabelaDeSimbolos.Estrutura.VARIAVEL)
                                        escopoAtual.adicionar_entrada_tabela_simbolos(entradaTabela)
                                        escopoAntigo.adicionar_tipo_nome(contexto.IDENT().getText(), entradaTabela)

                                        for s in regVars:
                                            escopoAtual.adicionar_tabela_simbolos(nomeId + '.' + s.nome, s.tipo, TabelaDeSimbolos.Estrutura.VARIAVEL)

            functionReturn = super().visitDeclaracao_global(contexto)
            self.escopos.abandonar_escopo()
        return functionReturn

    def visitCmdAtribuicao(self, ctx):
        tipoExpressao = Analisador.verificar_tipo_expressao(escopos=self.escopos, ctx=ctx.expressao())
        erro = False
        ponteiro = ''
        if ctx.getText()[0] == '^':
            ponteiro = "^"
        nomeVar = ''
        i = 0
        for ident in ctx.identificador().IDENT():
            if i > 0:
                nomeVar += '.'
            nomeVar += ident.getText()
            i += 1
        if tipoExpressao != TabelaDeSimbolos.TipoLA.INVALIDO:
            for escopo in self.escopos.obter_pilha():
                if escopo.contem(nomeVar):
                    tipoVar = Analisador.verificar_tipo_nome_var(escopos=self.escopos, nomeVar=nomeVar)
                    varNumeric = tipoVar == TabelaDeSimbolos.TipoLA.INTEIRO or tipoVar == TabelaDeSimbolos.TipoLA.REAL
                    expNumeric = tipoExpressao == TabelaDeSimbolos.TipoLA.INTEIRO or tipoExpressao == TabelaDeSimbolos.TipoLA.REAL
                    if not (
                            varNumeric and expNumeric) and tipoVar != tipoExpressao and tipoExpressao != TabelaDeSimbolos.TipoLA.INVALIDO:
                        erro = True
        else:
            erro = True

        if erro:
            nomeVar = ctx.identificador().getText()
            Analisador.adicionar_erro_semantico(ctx.identificador().start,
                                                    f'atribuicao nao compativel para {ponteiro + nomeVar}')

        return super().visitCmdAtribuicao(ctx)

    def visitTipo_basico_ident(self, contexto):
        if contexto.IDENT() is not None:
            nome_tipo = contexto.IDENT().getText()
            contem = any(escopo.contem(nome_tipo) for escopo in self.escopos.obter_pilha())
            if not contem:
                Analisador.adicionar_erro_semantico(contexto.start, f'tipo {nome_tipo} nao declarado')

        return super().visitTipo_basico_ident(contexto)

    def visitIdentificador(self, contexto):
        nomeVar = '.'.join(ident.getText() for ident in contexto.IDENT())
        erro = all(not escopo.contem(nomeVar) for escopo in self.escopos.obter_pilha())
        if erro:
            Analisador.adicionar_erro_semantico(contexto.start, f'identificador {nomeVar} nao declarado')
        return super().visitIdentificador(contexto)


    
    def visitCmdRetorne(self, contexto):
        if self.escopos.obter_escopo_atual().tipo == TabelaDeSimbolos.TipoLA.VOID:
            Analisador.adicionar_erro_semantico(contexto.start, f"comando retorne nao permitido nesse escopo")

        return super().visitCmdRetorne(contexto)