import os.path
import string
from analisadorLexico import AnalisadorLexico
from identificador import identificador

class analisadorSintatico():
    def __init__(self):
        lexico = AnalisadorLexico()
        lexico.analisar()
        self.tabelaSimbolos = lexico.tabelaSimbolos
        self.arquivo_entrada = open("tokens_teste", 'r')
        self.arquivo_saida = open("saida_sintatico", 'w')
        self.codigo_intermediario = open("codigo_intermediario", 'w')
        self.listTokens, self.tokensLinhas = self.getListTokens()
        self.indice = 0
        self.contexto = ''
        self.contextoPrincipal = '0'
        self.indiceContexto = 0
        self.intermediario = ''
        self.tmp1, self.tmp2, self.tmp3, self.op = '', '', '', ''
        self.indiceTemp = 0
        self.isWhile = False

    def salvarErro(self, msg):
        self.arquivo_saida.writelines(msg + ", linha: "+str(int(self.tokensLinhas[self.indice-1])) + ", token>>"+self.listTokens[self.indice-1] + '\n')

    def adicionarTipo(self, token, tipo):
        for i in self.tabelaSimbolos:
            if (i.id == token):
                i.tipo = tipo
                break
    
    def adicionarContexto(self, token):
        if (self.contexto == ''):
            self.contexto = self.contextoPrincipal
        for i in self.tabelaSimbolos:
            if (i.id == token):
                i.contexto = self.contexto
                break
    
    def incrementarContexto(self):                                      #token da função ou procedimento, caso seja um bloco, token = ''
        self.indiceContexto += 1                                        #incrementa o contexto
        if (self.contexto == ''):
            self.contexto = str(self.indiceContexto)
        else:
            self.contexto = self.contexto+'-'+str(self.indiceContexto)  #retorna contexto-novoContexto
    
    def decrementaContexto(self):
        v = self.contexto.split('-')
        v.pop()
        n = ''

        for i in v:
            n += str(i)+'-'
        self.contexto = n[0:len(n)-1]

    #verifica se o contexto passado como parametro
    #é valido no contexto atual
    def isContextoValido(self, contexto):                               #contexto do id na tabela de simbolos
        return contexto in self.contexto

    def getContexto(self, token):
        for i in self.tabelaSimbolos:
            if i.id == token:
                return i.contexto
        return 'E'                      #se o token não esta na tabela de simbolos, retorna E (um contexto inválido)

    def setFunctionTrue(self, token):
        for i in self.tabelaSimbolos:                       #pesquisa o token na tabela de simbolos
            if (i.id == token):                             #caso o identificador ja tenha sido declarado
                i.funcao = True
                return

    #retorna um token de uma linha
    def getToken(self, linha):
        texto = ""
        for i in linha:
            if i == "_":
                break
            texto += i
        return texto

    #retorna a lista de tokens
    def getListTokens(self):
        tokens = self.arquivo_entrada.readlines()
        listTokens = []
        tokensLinhas = []

        for i in tokens:
            listTokens.append(self.getToken(i))
            tokensLinhas.append(i.split('_')[2])
        listTokens.append('$')

        return listTokens, tokensLinhas

    #retorna a lista de parametros de uma função   
    def getListParam(self, tokenFunc):
        for i in self.tabelaSimbolos:
            if i.id == tokenFunc:
                return i.parametros

    #retorna o tipo do token
    def getTipoId(self, token):
        for i in self.tabelaSimbolos:                       #pesquisa o token na tabela de simbolos
            if (i.id == token):                             #caso o identificador ja tenha sido declarado
                return i.tipo                               #retorna o tipo do identificador
        return ""                                           #retorna string vazia caso o identificador não tenha sido declarado

    #incrementa o indice e retorna o proximo token de listToken
    def nextToken(self):                                    
        self.indice += 1
        return self.listTokens[self.indice]

    #retorna true se  o text for o token de um identificador
    def isId(self, text):
        if (text[0:2] == 'id'):
            return True
        return False
    
    #retorna true se o token representa uma função
    def isFunction(self, token):
        for i in self.tabelaSimbolos:                       #pesquisa o token na tabela de simbolos
            if (i.id == token):                             #caso o identificador ja tenha sido declarado
                return i.funcao                             #retorna true caso o token seja o token de uma função
        return False  

    #adiciona o indice do token na lista de parametros da função na tabela de simbolos
    def adicionarParametro(self, tokenFunc, token):
        tok     = -1
        tokFun  = -1
        indice  = 0

        for i in self.tabelaSimbolos:
            if (i.id == tokenFunc):                         #quando achar o token da função
                tokFun = indice  
            if (i.id == token):                             #quando achar o token do parametro
                tok = indice 
            if (tok != -1 and tokFun != -1):          #caso ja tenha achado os dois tokens
                break                                       #para o laço
            indice += 1
        
        if (tokFun != -1 and tok != -1):               
            self.tabelaSimbolos[tokFun].parametros.append(tok)

    #retorna true se o token passado como parametro for um operador boleano
    def operadorBool(self):
        token = self.listTokens[self.indice]

        operadores = "== != > >= < <= = !"
        if token in operadores.split():
            return True
        return False

    #retorna true se o token passado como parametro for umoperador aritimetico
    def operadorArit(self):
        token = self.listTokens[self.indice]
        operadores = "+ - * /"
        if token in operadores.split():
            return True
        return False

    #expressões aritimeticas
    def expressaoArit(self):
        token = self.listTokens[self.indice]
        flag  = self.isId(token) and self.getTipoId(token) == 'int'
        flag1 = flag and self.isContextoValido(self.getContexto(token))
        flag2 = flag and self.isFunction(token)
        valor = ''
        if (token == '('):
            token = self.nextToken()
            valor = self.expressaoArit()[1]
            token = self.listTokens[self.indice]
            if (token == ')'):
                token = self.nextToken()
                if (self.operadorArit()):
                    self.codeInterm(self.listTokens[self.indice])
                    token = self.nextToken()
                    return self.expressaoArit()
                return True, valor
            return False, ''
        elif (flag1 or flag2 or token == 'numero'):
            if (flag2):
                self._chamarFuncao()
            else:
                self.codeInterm(token)
                token = self.nextToken()
            if (self.operadorArit()):
                self.codeInterm(token)
                self.nextToken()
                return self.expressaoArit() 
            return True, valor #ja retorna no ;
        else:
            if (token != 'true' and token != 'false' and not(self.isFunction(token) and self.getTipoId(token) == 'bool')): #se for true ou false, pode ser a chemada em uma expressão boleana
                self.salvarErro("Erro de expressão aritmética")
            return False, ''    #caso a espressao esteja incompleta       
        
    #expressoes boleanas
    def expressaoBool(self):
        token = self.listTokens[self.indice]
        flag  = self.isId(token) and self.getTipoId(token) == 'bool'
        flag1 = flag and self.isContextoValido(self.getContexto(token)) #identificador do tipo booleano em um contexto valido
        flag2 = flag and self.isFunction(token)                         #função que retorna um booleano
        i     = self.indice 
        if(self.expressaoArit()):
            if(self.operadorBool()):    #caso o token atual seja um operador boleano
                token = self.listTokens[self.indice]
                if(token == "=="):
                    token = self.nextToken()
                    if (token == 'true' or token == 'false'):
                        token = self.nextToken()
                        return True
                else:
                    token = self.nextToken()
                if(self.expressaoArit()):
                    return True
        
        if (flag1 or flag2 or token == 'true' or token == 'false'):
            if(flag2):
                self._chamarFuncao()
            else:
                token = self.nextToken()

            if (self.operadorBool()):
                token = self.nextToken()
                flag  = self.isId(token) and self.getTipoId(token) == 'bool'
                flag1 = flag and self.isContextoValido(self.getContexto(token)) #identificador do tipo booleano em um contexto valido
                flag2 = flag and self.isFunction(token)                         #função que retorna um booleano
                if (flag1 or flag2 or token == 'true' or token == 'false'):
                    if(flag2):
                        self._chamarFuncao()
                    else:
                        token = self.nextToken()
                    return True
            else:
                return True

        self.salvarErro("Erro de expressão booleana")
        return False
    
    #lista de parametros para a chamada da função
    def listaParametrosChamada(self, tokenFunc, i):            #token da função
        token = self.listTokens[self.indice]
        lista = self.getListParam(tokenFunc)
        
        if (i < len(lista)):
            tipo  = self.tabelaSimbolos[lista[i]].tipo
            flag  = self.isId(token) and self.getTipoId(token) == tipo
            flag1 = flag and self.isContextoValido(self.getContexto(token)) 
            flag2 = token == 'numero' and tipo == 'int'
            flag3 = tipo == 'bool' and (token == 'true' or token == 'false')
            flag4 = flag and self.isFunction(token)

            if (flag1 or flag2 or flag3 or flag4):
                if(flag4):
                    self._chamarFuncao()
                    token = self.listTokens[self.indice]
                else:
                    token = self.nextToken()
                i += 1
                if(token == ','):
                    token = self.nextToken()
                    if (self.isId(token) or token == 'numero' or token == 'true' or token == 'false'):
                        return self.listaParametrosChamada(tokenFunc, i)
                elif(token == ')' and i == len(lista)):
                    return True
        elif (i == len(lista)):
            if(token == ')'):
                    return True
        self.salvarErro("Erro de lista de parametros da chamada da função ou procedimento")
        return False

    #lista de parametros para a declaração de funções
    def listaParametros(self, tokenFunc):
        token = self.listTokens[self.indice]

        if (token == 'int' or token == 'bool'):
            tipo = token
            token = self.nextToken()
            self.adicionarContexto(token)
            if(self.isId(token)):
                self.adicionarTipo(token, tipo)                 #adiciona tipo ao identificador
                self.adicionarParametro(tokenFunc, token)       #adiciona o parametro a função na tabela de simbolos
                token = self.nextToken()
                if (token == ','):
                    token = self.nextToken()
                    if (token == 'int' or 'bool'):  #é verificado novamente para não ser possivel colocar algo do tipo (.... int a;)
                        return self.listaParametros(tokenFunc)
                elif(token == ')'):
                    return True
        elif(token == ')'):         #lista de parametros vazia
            return True
        self.salvarErro("Erro de lista de parametros")
        return False

    #declaração de funções
    def _funcao(self, tokenFunc):
        token = self.nextToken()
        if(self.listaParametros(tokenFunc)):
            token = self.nextToken()
            if (token == '{'):
                token = self.nextToken()
                if(token != 'return'):
                    while(self._s()):
                        token = self.nextToken()
                        if (token == 'return'):
                            break

                if  (token == 'return'):
                    token = self.nextToken()
                    tipo = self.getTipoId(tokenFunc)    #tipo recebe o tipo da função
                    tokenId = False                     #flag para identificar se o retorno é um id
                    tipoToken = ''                      #tipo do id que esta sendo retornado
                    flag1 = (tipo == 'bool' and (token == 'true' or token == 'false'))
                    flag2 = tipo == 'int' and token == 'numero'

                    if(self.isId(token)):                   #se o token for um identificador
                        tipoToken = self.getTipoId(token)   #tipoToken recebe o tipo do identificador
                        tokenId = True                      #identifica que o retorno é um id
                    if((tokenId == True and tipo == tipoToken) or flag1 or flag2):
                        if(tokenId and not self.isContextoValido(self.getContexto(token))):  #se a variavel nao esta em um contexto valido
                            self.salvarErro("Erro de função. Variavel retorna não foi declarada no escopo da função")
                            return False
                        token = self.nextToken()
                        if (token == ';'):
                            token = self.nextToken()
                            if(token == '}'):
                                self.decrementaContexto()
                                return True 
                    
        self.salvarErro("Erro de função")
        return False

    #declaração de procedimento
    def _procedimento(self, tokenProc):
        token = self.nextToken()
        if(self.listaParametros(tokenProc)):
            token = self.nextToken()
            if (token == '{'):
                token = self.nextToken()
                while(self._s()):
                    token = self.nextToken()
                    if (token == '}'):
                        self.decrementaContexto()
                        return True                    
        self.salvarErro("Erro de procedimento")
        return False

    #declaração de variaveis e funções
    def _declaracao(self):
        tipo = self.listTokens[self.indice]
        token = self.nextToken()
        tokenId = token #id do token que será atribuido
        self.codeInterm('temp'+str(self.indiceTemp))
        self.indiceTemp += 1
        if (self.isId(token)):
            self.adicionarTipo(token, tipo)                     #adiciona o tipo na tabela de simbolos
            token = self.nextToken()
            if (token == '(' and self.isWhile == False):        #se for uma função ou um procedimento e nao estaja dentro de um while.
                if (self.contexto == self.contextoPrincipal or self.contexto == ''):   #se estiver no contexto principal                                           
                    self.contexto = ''
                    self.incrementarContexto()                  #incrementa o contexto
                    self.adicionarContexto(tokenId)             #adiciona o contexto na tabela de simbolos
                    if (tipo == 'void'):                        #caso seja um procedimento
                        return self._procedimento(tokenId)      #retornará True caso a sintaxe do procedimento esteja correto.
                    self.setFunctionTrue(tokenId)               #caso não seja um procedimento, adiciona funcao = true para este token na tabela de simbolos
                    return self._funcao(tokenId)                #retornará True caso a sintaxe da função esteja correta
            elif (token == '='):                                #se for a atribuição de uma variavel
                self.adicionarContexto(tokenId)                 #adiciona o contexto na tabela de simbolos
                self.codeInterm(token)
                return self._atribuicao(tipo, tokenId)          #chama a atribuição
            elif(token == ';'):                                 #se for uma declaração de variavel, sem atribuição
                self.adicionarContexto()                        #adiciona o contexto na tabela de simbolos
                return True                                     #retorna true (declaração sem atribuição)
        self.salvarErro("Erro de declaração")
        return False

    #print
    def _print(self):
        token = self.nextToken()
        toknId = False
        flag = False

        if (self.isId(token)):
            tokenId = True
            if (self.isContextoValido(self.getContexto(token))):
                flag = True
            else:
                print('contexto invalido')


        if (flag == True or token == 'numero'):
            token = self.nextToken()
            if(token == ';'):
                return True
        self.salvarErro("Erro no print")
        return False

    #if
    def _if(self):
        token = self.nextToken()
        self.incrementarContexto()
        if (token == '('):
            token = self.nextToken()
            if (self.expressaoBool()):
                token = self.listTokens[self.indice]
                if (token == ')'):
                    token = self.nextToken()

                    if (token == '{'):
                        token = self.nextToken()
                        while (self._s()):
                            token = self.nextToken()
                            if (token == '}'):
                                self.decrementaContexto()
                                return True
        self.salvarErro("Erro de desvio condicional")
        return False
    
    def _else(self):
        token = self.nextToken()
        self.incrementarContexto()
        if (token == '{'):
            token = self.nextToken()
            while (self._s()):
                token = self.nextToken()
                if (token == '}'):
                    self.decrementaContexto()
                    return True
        self.salvarErro("Erro de desvio condicional")
        return False
    

    def _while(self):
        token = self.nextToken()
        self.incrementarContexto()
        if (token == '('):
            token = self.nextToken()
            ehExpBool = self.expressaoBool()
            if (ehExpBool):
                token = self.listTokens[self.indice]    
                if (token == ')'):
                    token = self.nextToken()
                    if (token == '{'):
                        token = self.nextToken()
                        self.isWhile = True
                        while (self._s()):
                            self.isWhile = True
                            token = self.nextToken()
                            if (token == '}'):
                                self.isWhile = False
                                self.decrementaContexto()
                                return True
        self.salvarErro("Erro de laço")
        return False

    def _chamarFuncao(self):
        tokenFunc = self.listTokens[self.indice]
        token = self.nextToken()
        if (token == '('):
            token = self.nextToken()
            if (self.listaParametrosChamada(tokenFunc, 0)):
                token = self.nextToken()
                return True

        self.salvarErro("Erro na chamada de função")
        return False

    def _chamarProcedimento(self):
        tokenFunc = self.listTokens[self.indice]
        token = self.nextToken()
        if (token == '('):
            token = self.nextToken()
            if (self.listaParametrosChamada(tokenFunc, 0)):
                token = self.nextToken()
                if (token == ';'):
                    return True
        self.salvarErro("Erro na chamada do procedimento")
        return False

    def escreverIntermediario(self):                                    
        self.codigo_intermediario.writelines(self.tmp1+':='+self.tmp2+self.op+self.tmp3+'\n')   #escreve o codigo no arquivo
        self.tmp1 = ''
        self.tmp2 = ''
        self.tmp3 = '' 

    def codeInterm(self, token):
        flag1 = self.tmp1 != ''
        flag2 = self.tmp2 != ''
        flag3 = self.tmp3 != ''

        i = self.intermediario.split(' ')
        if (token == ';' or  (flag1 and flag2 and flag3)):
            self.escreverIntermediario()

        if (token != ';'):
            if(self.tmp1 == ''):
                self.tmp1 = token
            elif(self.tmp2 == ''):
                self.tmp2 = token
            elif(self.op == ''):
                self.tmp3 = token
            elif(self.tmp3 == ''):
                self.tmp3 = token

    def setValor(self, token, valor):
        for i in self.tabelaSimbolos:
            if i.id == token:
                i.valor = valor

    def _atribuicao(self, tipo, tokenId):
        token = self.nextToken()
        flag = False
        self.codeInterm(tokenId)
        valor = ''

        if (tipo == 'bool'):
            flag = self.expressaoBool()
            token = self.listTokens[self.indice]
        elif (tipo == 'int'):
            flag, valor = self.expressaoArit()   
            token = self.listTokens[self.indice]
        if (token == ';' and flag == True):
            self.codeInterm(tokenId)
            self.setValor(tokenId, valor)
            return True
        self.salvarErro("Erro de atribuição")
        return False

    def _s(self):
        token = self.listTokens[self.indice]
        if ( token == 'int' or token == 'bool' or token == 'void'):        #declarações
            if (self._declaracao() == True):
                return True
            self.salvarErro("Erro de declaração")
            return False
        if (token == 'print'):
            return self._print()
        
        if (token == 'if'):
            return self._if()

        if (token == 'ifelse'): # o corpo do if eh parecido
            return self._if()

        if (token == 'else'):
            return self._else()
            
        if (token == 'while'):
            return self._while()
        
        if (token == 'break' or token == 'continue' ):
            token = self.nextToken()
            
            if (token == ';'):
                if(self.isWhile):
                    return True
                else:
                    self.salvarErro("Erro de desvio condicional. Uso fora do loop!")
                    return False
            else:
                self.salvarErro("Erro de desvio condicional")
                return False
        
        if (self.isId(token)):
            tipo = self.getTipoId(token)
            prox_token = self.listTokens[self.indice+1]  
            if (prox_token == '='):
                if (self.isContextoValido(self.getContexto(token))):
                    token = self.nextToken()
                    return self._atribuicao(tipo, self.listTokens[self.indice-1])
            else:
                for i in self.tabelaSimbolos:                       #pesquisa o token na tabela de simbolos
                    if (i.id == token):                             #caso o identificador ja tenha sido declarado
                        if (i.tipo == 'void'):                      #e ele seja um procedimento
                            return self._chamarProcedimento()       #chama o procedimento
                        else:                                       #caso não seja um procedimento    
                            flag = self._chamarFuncao()             #chama a função
                            if (flag == False):
                                return False
                            token = self.listTokens[self.indice]
                            if(token == ';'):
                                return True
                            else:
                                self.salvarErro("Erro na chamada da função")
                                return False
                        break
            
        self.salvarErro("ERRO na analise!")
        return False
            
    def inicio(self):
        while (True):
            if (self.indice < len(self.listTokens) -1):
                if (self._s() == False): #chamar a função inicial, que irá percorrer os tokens recursivamente
                    print ('ERRO na analise!\n') 
                    self.arquivo_saida.close()  
                    self.arquivo_saida = open("saida_sintatico", 'r')
                    erros = self.arquivo_saida.readlines()
                    for i in erros:
                        print(i)
                    break
                self.nextToken()
            else:
                print ('SUCESSO na analise!\n')
                break
    
        self.arquivo_entrada.close()
        self.arquivo_saida.close()  

        for i in self.tabelaSimbolos:
            print(i.lexema+' ----- valor = ' +i.valor)

analisador = analisadorSintatico()
analisador.inicio()