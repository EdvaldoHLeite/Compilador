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
        self.listTokens, self.tokensLinhas, self.lexemas = self.getListTokens()
        self.indice = 0
        self.contexto = ''
        self.contextoPrincipal = '0'
        self.indiceContexto = 0
        self.tmp = 'tmp'
        self.indiceTemp = 0
        self.isWhile = False
        
        # desvio condicional - codigo intermediario
        self.identResultBool = None # variavel que salva o ultimo identificador, resultado de uma expressao booleana
        self.contadorIf = 0 # conta os if-elifs-else
        self.desviosAtuais = list() # pilha de desvios condicionais abertos
        self.contadorDesvioCondicional = 0 # conta os desvios condicionais
        
        
        # while - codigo intermediario
        self.contadorWhile = 0
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
        lexemas = []
        for i in tokens:
            v = i.split('_')
            listTokens.append(self.getToken(i))
            tokensLinhas.append(v[2])
            lexemas.append(v[1])
        listTokens.append('$')

        return listTokens, tokensLinhas, lexemas

    #retorna o lexema do token atual
    def getLexema(self):
        return self.lexemas[self.indice]

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

    #verifica se o simbolo é um operador booleano
    def isOperadorBool(self, simbol):
        operadores = "== != > >= < <= = !"
        if simbol in operadores.split():
            return True
        return False

    #retorna true se o token passado como parametro for um operador boleano
    def operadorBool(self):
        return self.isOperadorBool(self.listTokens[self.indice])

    #retorna true se o token passado como parametro for umoperador aritimetico
    def operadorArit(self):
        token = self.listTokens[self.indice]
        operadores = "+ - * /"
        if token in operadores.split():
            return True
        return False

    #expressões aritimeticas
    def expressaoArit(self, ident, simbol):
        token = self.listTokens[self.indice]
        flag  = self.isId(token) and self.getTipoId(token) == 'int'
        flag1 = flag and self.isContextoValido(self.getContexto(token))
        flag2 = flag and self.isFunction(token)

        if (token == '('):
            simbol.append(token)
            token = self.nextToken()
            self.expressaoArit(ident, simbol)
            token = self.listTokens[self.indice]
            if (token == ')'):
                simbol.append(token)
                token = self.nextToken()
                if (self.operadorArit()):
                    simbol.append(token)
                    token = self.nextToken()
                    return self.expressaoArit(ident, simbol)
                return True
            return False, ''
        elif (flag1 or flag2 or token == 'numero'):
            if (flag2):                                             #caso seja uma função
                self._chamarFuncao()
                #ident.append(self.getValor(token))
            else:
                if(flag1):                      #caso seja um identificador                           
                    ident.append(token)         #adiciona o identificador
                else:                                   #caso seja um valor inteiro (token == num)
                    ident.append(self.getLexema()) #adiciona o lexema
                token = self.nextToken()
            if (self.operadorArit()):
                simbol.append(token)
                self.nextToken()
                return self.expressaoArit(ident, simbol) 
            return True #ja retorna no ;
        else:
            if (token != 'true' and token != 'false' and not(self.isFunction(token) and self.getTipoId(token) == 'bool')): #se for true ou false, pode ser a chemada em uma expressão boleana
                self.salvarErro("Erro de expressão aritmética")
            return False, ''    #caso a espressao esteja incompleta       
        
    def expressaoBool(self, ident, simbol):
        token = self.listTokens[self.indice]
        flag  = self.isId(token) and self.getTipoId(token) == 'bool'
        flag1 = flag and self.isContextoValido(self.getContexto(token)) #identificador do tipo booleano em um contexto valido
        flag2 = flag and self.isFunction(token)                         #função que retorna um booleano
        i     = self.indice 

        if(self.expressaoArit(ident, simbol)):#se o primeiro termo for uma expressão aritmetica
            if(self.operadorBool()):                                    #caso o token atual seja um operador boleano
                token = self.listTokens[self.indice]
                simbol.append(token)
                if(token == "=="):
                    token = self.nextToken()
                    if (token == 'true' or token == 'false'):
                        ident.append(token)
                        token = self.nextToken()
                        return True                        
                else:
                    token = self.nextToken()
                if(self.expressaoArit(ident, simbol)):
                    return True
        
        if (flag1 or flag2 or token == 'true' or token == 'false'):#se o primeiro termo for um identificador boleano ou true ou false
            ident.append(token)
            if(flag2):                                  #se for uma função
                self._chamarFuncao()                    #chama a função
                token = self.listTokens[self.indice]    #token recebebe o token atual
            else:#caso seja uma variavel boleana ou true ou false
                token = self.nextToken()#token recebe o proximo token

            if (self.operadorBool()):#se for um operador boleano
                simbol.append(token)    #adiciona o simbolo boelano na tabela
                token = self.nextToken() #passa para o proximo token
                flag  = self.isId(token) and self.getTipoId(token) == 'bool'
                flag1 = flag and self.isContextoValido(self.getContexto(token)) #identificador do tipo booleano em um contexto valido
                flag2 = flag and self.isFunction(token)                         #função que retorna um booleano
                if (flag1 or flag2 or token == 'true' or token == 'false'):
                    ident.append(token)
                    if(flag2):
                        self._chamarFuncao()
                        token = self.listTokens[self.indice]
                    else:
                        token = self.nextToken()
                    return True
            else:
                return True

        self.salvarErro("Erro de expressão booleana")
        return False
    
    #lista de parametros para a chamada da função
    def listaParametrosChamada(self, tokenFunc, i, lexFunc):            #token da função
        token = self.listTokens[self.indice]
        lista = self.getListParam(tokenFunc)
        
        if (i < len(lista)):
            tipo  = self.tabelaSimbolos[lista[i]].tipo
            flag  = self.isId(token) and self.getTipoId(token) == tipo
            flag1 = flag and self.isContextoValido(self.getContexto(token)) 
            flag2 = token == 'numero' and tipo == 'int'
            flag3 = tipo == 'bool' and (token == 'true' or token == 'false')
            flag4 = flag and self.isFunction(token)
            #  1)token é um id valido
            #  2)token é um numero
            #  3)token é true ou false
            #  4)token é uma função
            if (flag1 or flag2 or flag3 or flag4):
                if(flag4):
                    self._chamarFuncao()
                    self.codigo_intermediario.writelines('param tmp'+str(self.indiceTemp - 1)+'\n')
                    token = self.listTokens[self.indice]
                else:
                    #codigo de três endereços: (adicionando os parametros)
                    if(flag1 or flag3):
                        self.codigo_intermediario.writelines('param '+token+'\n')
                    else:
                        self.codigo_intermediario.writelines('param '+self.getLexema()+'\n')
                    #passa para o proximo token e continua a chamada da função
                    token = self.nextToken()
                i += 1
                if(token == ','):
                    token = self.nextToken()
                    if (self.isId(token) or token == 'numero' or token == 'true' or token == 'false'):
                        return self.listaParametrosChamada(tokenFunc, i, lexFunc)
                elif(token == ')' and i == len(lista)):
                    self.codigo_intermediario.writelines('tmp'+str(self.indiceTemp)+' := call '+lexFunc+', '+str(i)+'\n')
                    self.indiceTemp += 1
                    return True
        elif (i == len(lista)):
            if(token == ')'):
                    self.codigo_intermediario.writelines('tmp'+str(self.indiceTemp)+' := call '+lexFunc+', '+str(i)+'\n')
                    self.indiceTemp += 1
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

        #usado no final da expressão
    
    def escreverIntermediarioAtribuicao(self, variavel, temp):
        codigo = variavel+' := '+temp+'\n'
        self.codigo_intermediario.writelines(codigo)
        self.setValor(variavel, temp)
    
    #usado durante a expressão
    def escreverIntermediario(self, esq, sim, dire): 
        self.tmp = 'tmp'+str(self.indiceTemp)               #tmp atual que será escrito no arquivo
        self.indiceTemp = self.indiceTemp + 1               #incrementa o proximo tmp
        codigo = self.tmp+' := '+ esq +' '+ sim + ' ' + dire +'\n'
        self.codigo_intermediario.writelines(codigo)   #escreve o codigo no arquivo

    #monta a string que vai ser escrita no arquivo do codigo de tres endereços
    #e retira os elementos dos vetores ident e simbol
    def tresEnderecos(self, ident, simbol, i):
        if (len(ident) > i+1):
            esq = ident[i]
            sim = simbol[i]
            dire = ident[i+1]
            self.escreverIntermediario(esq, sim, dire)
            ident[i] = self.tmp
            ident.pop(i+1)
            simbol.pop(i)
            return True
        else:
            self.salvarErro('Erro na formação da expressão')
            return False

    #escreve o codigo intermediario para expressões aritimeticas de acordo com um vetor de identificadores/numeros 
    #e um vetor de simbolos   
    def codeIntermExpArit(self, token, ident, simbol, indice):
        i = indice
    
        while (i < len(simbol)):                                    #procura por expressões dentro de parenteses
            if (simbol[i] == '('):                                  #caso ache
                simbol.pop(i)                                       #retira o simbolo do vetor    
                self.codeIntermExpArit(token, ident, simbol, i)     #chama recursivamente a função para a expressão dentro dos parenteses
            else:
                i = i+1
        #após verificar por expressões dentro de parenteses, procura por multiplicações e divisões dentro da expressão
        i = indice

        while (i < len(simbol)):
            if (simbol[i] == '*' or simbol[i] == '/'):
                if (self.tresEnderecos(ident, simbol, i) == False):
                    return False
            elif (simbol[i] == ')'):
                    break
            else:
                i = i+1
        #após verificar multiplicações e divisões na expressão, procura por soma e subtração
        i = indice

        while (i < len(simbol)):
            if (simbol[i] == '+' or simbol[i] == '-'):
                if (self.tresEnderecos(ident, simbol, i) == False):
                    return False
            elif (simbol[i] == ')'):
                    simbol.pop(i)
                    return
            else:
                i = i+1
        
        #no caso de expressões boleanas, "sobram" 2 elementos em ident e um em simbol (o operador boleano)
        if (len(simbol) == 1 and self.isOperadorBool(simbol[0]) and len(ident) == 2):
            self.tresEnderecos(ident, simbol, 0)

        if (len(simbol) == 0 and len(ident) == 1):
            self.escreverIntermediarioAtribuicao(token, ident[0])       #escreve a ultima linha do codigo de três endereços para a expressão
        else:
            self.salvarErro('Erro na formação da expressão. Erro ao tentar escrever codigo intermediario')
            return False 

    def setValor(self, token, valor):
        for i in self.tabelaSimbolos:
            if i.id == token:
                i.valor = valor
                return
    
    #retorna o valor do token na tabela de simbolos
    def getValor(self, token):
        for i in self.tabelaSimbolos:
            if i.id == token:
                return i.valor
    
    #declaração de funções
    def _funcao(self, tokenFunc):
        token = self.nextToken()
        ident = list()
        simbol = list()
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
                    
                    if (tipo == 'bool'):
                        self.expressaoBool(ident, simbol)
                            
                    if(tipo == 'int'):
                        self.expressaoArit( ident, simbol)
                    
                    self.codeIntermExpArit(tokenFunc, ident, simbol, 0)    
                    token = self.listTokens[self.indice]

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
                return self._atribuicao(tipo, tokenId)          #chama a atribuição
            elif(token == ';'):                                 #se for uma declaração de variavel, sem atribuição
                self.adicionarContexto(tokenId)                 #adiciona o contexto na tabela de simbolos
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
            lexema = self.lexemas[self.indice]
            token = self.nextToken()
            if(token == ';'):
                self.codigo_intermediario.writelines("print " + lexema + "\n")
                return True
        self.salvarErro("Erro no print")
        return False

    #if
    def _if(self):
        token = self.nextToken()
        self.incrementarContexto()
        ident = list()
        simbol = list()
        
        # sequencias de ifs tem mais um if
        self.contadorIf += 1
        
        if (token == '('):
            token = self.nextToken()
            if (self.expressaoBool(ident, simbol)):
                
                # salva a linha de chamada do if aninhado
                chamadaIf = "iffalse "+str(self.identResultBool)+" goto fimIF"+str(self.contadorIf) + "\n"
                self.codigo_intermediario.writelines(chamadaIf)
                
                token = self.listTokens[self.indice]
                if (token == ')'):
                    token = self.nextToken()  
                    self.guardarIf = True # começa a guardar codigo intermediario do corpo
                    if (token == '{'):
                        token = self.nextToken()
                        while (self._s()):                            
                            token = self.nextToken()
                            if (token == '}'):
                                self.guardarIf = False
                                self.decrementaContexto()
                                # goto para label do desvio condicional e finalizacao do if
                                self.codigo_intermediario.writelines("goto L_IF" + str(self.desviosAtuais[len(self.desviosAtuais)-1]) + "\n")
                                self.codigo_intermediario.writelines("fimIF" + str(self.contadorIf) + ":\n")
                                self.fecharDesvioCondicional()
                                return True
                        
        self.salvarErro("Erro de desvio condicional")
        return False
    
    ### verifica se nao existe outro condicional
    def fecharDesvioCondicional(self):
        prox_token = self.listTokens[self.indice+1] 
        if (prox_token != 'ifelse' and prox_token != 'else'): # sequencias de ifs chegam ao fim
            self.codigo_intermediario.writelines("L_IF" + str(self.desviosAtuais[len(self.desviosAtuais)-1]) + ":\n") # label final do desvio condicional
            self.desviosAtuais.pop() # remove o desvio condicional atual da pilha
        
    
    def _else(self):
        # sequencia de ifs tem mais um
        self.contadorIf += 1
        
        token = self.nextToken()
        self.incrementarContexto()
        
        # salva a linha de chamada do if aninhado
        #chamadaIf = "goto L"+str(self.contadorIf) + "\n"
        #self.codigo_intermediario.writelines(chamadaIf)
        
        self.guardarIf = True
        if (token == '{'):
            token = self.nextToken()
            while (self._s()):
                token = self.nextToken()
                if (token == '}'):
                    self.decrementaContexto()
                    self.codigo_intermediario.writelines("goto L_IF" + str(self.desviosAtuais[len(self.desviosAtuais)-1]) + "\n")
                    self.codigo_intermediario.writelines("fimIF" + str(self.contadorIf) + ":\n")
                    self.fecharDesvioCondicional()
                    return True
        self.salvarErro("Erro de desvio condicional")
        return False
    
    def _while(self):
        token = self.nextToken()
        self.incrementarContexto()
        ident = list()
        simbol = list()
        
        self.contadorWhile += 1 # incrementa o contador de while
        labelInicio = "W" + str(self.contadorWhile)
        labelSaida = "Wfim" + str(self.contadorWhile) # label para saida e finalizacao do while
        
        if (token == '('):
            token = self.nextToken()
            self.codigo_intermediario.writelines(labelInicio + ":\n")
            ehExpBool = self.expressaoBool(ident, simbol)
            if (ehExpBool):
                token = self.listTokens[self.indice]    
                if (token == ')'):
                    self.codigo_intermediario.writelines("iffalse " + str(self.identResultBool) + " goto " + labelSaida + "\n")
                    
                    token = self.nextToken()
                    if (token == '{'):
                        token = self.nextToken()
                        if (token == '}'):
                            self.salvarErro("Erro de laço. O laço while esta vazio (loop infinito!).")
                            return False
                        self.isWhile = True
                        while (self._s()):
                            self.isWhile = True
                            token = self.nextToken()
                            if (token == '}'):
                                self.isWhile = False
                                self.decrementaContexto()
                                
                                self.codigo_intermediario.writelines("goto " + labelInicio + "\n")
                                self.codigo_intermediario.writelines(labelSaida+":\n") # label de saida do whiles
                                
                                return True
        self.salvarErro("Erro de laço")
        return False

    def _chamarFuncao(self):
        tokenFunc = self.listTokens[self.indice]
        lexFunc = self.getLexema()
        token = self.nextToken()
        if (token == '('):
            token = self.nextToken()
            if (self.listaParametrosChamada(tokenFunc, 0, lexFunc)):
                token = self.nextToken()
                return True

        self.salvarErro("Erro na chamada de função")
        return False

    def _chamarProcedimento(self):
        tokenFunc = self.listTokens[self.indice]
        lexFunc = self.getLexema()
        token = self.nextToken()
        if (token == '('):
            token = self.nextToken()
            if (self.listaParametrosChamada(tokenFunc, 0, lexFunc)):
                token = self.nextToken()
                if (token == ';'):
                    return True
        self.salvarErro("Erro na chamada do procedimento")
        return False

    def _atribuicao(self, tipo, tokenId):
        token = self.nextToken()
        ident = list()
        simbol = list()
        flag = False

        if (tipo == 'bool'):
            flag = self.expressaoBool(ident, simbol)
            token = self.listTokens[self.indice]
        elif (tipo == 'int'):
            flag  = self.expressaoArit(ident, simbol)   
            token = self.listTokens[self.indice]
        if (token == ';' and flag == True):
            self.codeIntermExpArit(tokenId, ident, simbol, 0)   #ident e simbol são preenchidos em expressaoArit
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
            self.contadorDesvioCondicional += 1
            self.desviosAtuais.append(self.contadorDesvioCondicional) # adiciona o desvio condicional atual na pilha
            return self._if()

        if (token == 'ifelse'): # o corpo do if eh parecido
            return self._if()

        if (token == 'else'):
            return self._else()
            
        if (token == 'while'):
            return self._while()
        
        if (token == 'break' or token == 'continue' ):
            desvio = token
            token = self.nextToken()
            
            if (token == ';'):
                if(self.isWhile):
                    
                    if (desvio == 'break'): # vai para o label final do while
                        self.codigo_intermediario.writelines("goto Wfim" + str(self.contadorWhile) + "\n")
                    elif (desvio == 'continue'):
                        self.codigo_intermediario.writelines("goto W" + str(self.contadorWhile) + "\n")
                    
                    return True
                else:
                    self.salvarErro("Erro de desvio condicional. Uso fora do loop!")
                    return False

            else:
                self.salvarErro("Erro de desvio incondicional")
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

        #for i in self.tabelaSimbolos:
            #print(i.lexema+' ----- valor = ' +i.valor)

analisador = analisadorSintatico()
analisador.inicio()