import os.path
import string
from analisadorLexico import AnalisadorLexico

class analisadorSintatico():
    def __init__(self):
        lexico = AnalisadorLexico()
        lexico.analisar()
        self.tabelaSimbolos = lexico.tabelaSimbolos
        self.arquivo_entrada = open("tokens_teste", 'r')
        self.arquivo_saida = open("saida_sintatico", 'w')
        self.listTokens, self.tokensLinhas = self.getListTokens()
        self.indice = 0


    def salvarErro(self, msg):
        self.arquivo_saida.writelines(msg + ", linha: "+str(int(self.tokensLinhas[self.indice])) + ", token>>"+self.listTokens[self.indice] + '\n')

    def adicionarTipo(self, token, tipo):
        indice = token[2:]
        self.tabelaSimbolos[int(indice)-1].tipo = tipo

    #retorna um token de uma linha
    def getToken(self, linha):
        texto = ""
        for i in linha:
            if i == "_":
                break
            texto += i
        return texto

    def getListTokens(self):
        tokens = self.arquivo_entrada.readlines()
        listTokens = []
        tokensLinhas = []

        for i in tokens:
            listTokens.append(self.getToken(i))
            tokensLinhas.append(i.split('_')[2])
        listTokens.append('$')

        return listTokens, tokensLinhas

    def nextToken(self):    #incrementa o indice e retorna o proximo token de listToken
        self.indice += 1
        return self.listTokens[self.indice]

    def isId(self, text):
        if (text[0:2] == 'id'):
            return True
        return False

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

        if (token == '('):
            token = self.nextToken()
            self.expressaoArit()
            token = self.listTokens[self.indice]
            if (token == ')'):
                token = self.nextToken()
                if (self.operadorArit()):
                    token = self.nextToken()
                    return self.expressaoArit()
                return True
            return False

        elif (self.isId(token) or token == 'numero'):
            token = self.nextToken()
            #verificar se id é um inteiro
            if (self.operadorArit()):
                token = self.nextToken()
                return self.expressaoArit()
            return True #ja retorna no ;
        else:
            if (token != 'true' and token != 'false'): #se for true ou false, pode ser a chemada em uma expressão boleana
                self.salvarErro("Erro de expressão aritmética")
            return False    #caso a espressao esteja incompleta       
        


    #expressoes boleanas
    def expressaoBool(self):
        token = self.listTokens[self.indice]
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
        elif (token == 'true' or token == 'false'):
            return True

        self.salvarErro("Erro de expressão booleana")
        return False
    
    def listaParametrosChamada(self):
        token = self.listTokens[self.indice]

        if (self.isId(token) or token == 'numero' or token == 'true' or token == 'false'):
            token = self.nextToken()
            if(token == ','):
                token = self.nextToken()
                if (self.isId(token) or token == 'numero' or token == 'true' or token == 'false'):
                    return self.listaParametrosChamada()
            elif(token == ')'):
                return True
        elif(token == ')'):         #lista de parametros vazia
            return True
        self.salvarErro("Erro de lista de parametros da chamada da função")
        return False


    #lista de parametros para a declaração de funções
    def listaParametros(self):
        token = self.listTokens[self.indice]

        if (token == 'int' or token == 'bool'):
            token = self.nextToken()
            if(self.isId(token)):
                token = self.nextToken()
                if (token == ','):
                    token = self.nextToken()
                    if (token == 'int' or 'bool'):  #é verificado novamente para não ser possivel colocar algo do tipo (.... int a;)
                        return self.listaParametros()
                elif(token == ')'):
                    return True
        elif(token == ')'):         #lista de parametros vazia
            return True
        self.salvarErro("Erro de lista de parametros")
        return False

    #declaração de funções
    def _funcao(self):
        token = self.nextToken()
        if(self.listaParametros()):
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
                    if(self.isId(token) or token == 'true' or token == 'false' or token == 'numero'):
                        token = self.nextToken()
                        if (token == ';'):
                            token = self.nextToken()
                            if(token == '}'):
                                return True 
                    
        self.salvarErro("Erro de função")
        return False


    #declaração de variaveis e funções
    def _declaracao(self):
        tipo = self.listTokens[self.indice]
        token = self.nextToken()
        if (self.isId(token)):
            self.adicionarTipo(token, tipo)  #adiciona o tipo na tabela de simbolos
            token = self.nextToken()

            if (token == '('):               #se for uma função
                return self._funcao()        #retornará True caso o sintaxe da função esteja correta
            elif (token == '='):             #se for a atribuição de uma variavel
                token = self.nextToken()
                if (tipo == 'bool' and self.expressaoBool()):
                    token = self.listTokens[self.indice]
                    if (token == ';'):
                        return True

                elif ((token == 'numero' and tipo == 'int') or (token == 'true' and tipo == 'bool') or (token == 'false' and tipo == 'bool')):
                    token = self.nextToken()
                    if (token == ';'):
                        return True
            elif(token == ';'):               #se for uma declaração de variavel, sem atribuição
                return True
        self.salvarErro("Erro de declaração")
        return False

    #print
    def _print(self):
        token = self.nextToken()
        if (self.isId(token) or token == 'numero'):
            token = self.nextToken()
            if(token == ';'):
                return True
        self.salvarErro("Erro no print")
        return False

    #if
    def _if(self):
        token = self.nextToken()

        if (token == '('):
            token = self.nextToken()
            if (self.expressaoBool()):
                token = self.listTokens[self.indice]
                #token = self.nextToken()
                if (token == ')'):
                    token = self.nextToken()

                    if (token == '{'):
                        token = self.nextToken()
                        while (self._s()):
                            token = self.nextToken()
                            if (token == '}'):
                                return True
        self.salvarErro("Erro de desvio condicional")
        return False
    
    def _else(self):
        token = self.nextToken()
        if (token == '{'):
            token = self.nextToken()
            while (self._s()):
                token = self.nextToken()
                if (token == '}'):
                    return True
        self.salvarErro("Erro de desvio condicional")
        return False
    
    def _while(self):
        token = self.nextToken()
        if (token == '('):
            token = self.nextToken()
            ehExpBool = self.expressaoBool()
            if (ehExpBool):
                token = self.listTokens[self.indice]    
                if (token == ')'):
                    token = self.nextToken()
                    if (token == '{'):
                        token = self.nextToken()
                        while (self._s()):
                            token = self.nextToken()
                            if (token == '}'):
                                return True
        self.salvarErro("Erro de laço")
        return False

    def _chamarFuncao(self):
        token = self.nextToken()
        if (token == '('):
            token = self.nextToken()
            if (self.listaParametrosChamada()):
                token = self.nextToken()
                if (token == ';'):
                    return True
        self.salvarErro("Erro na chamada de função")
        return False

    def _atribuicao(self):
        token = self.nextToken()
        if (token == '='):
            token = self.nextToken()
            if (self.isId(token) or token == 'numero' or token == 'true' or token == 'false'):
                if (self.isId(token) and self._chamarFuncao()):
                    return True
                token = self.nextToken()
                if (token == ';'):
                    return True
        self.salvarErro("Erro de atribuição")
        return False

    def _s(self):
        token = self.listTokens[self.indice]
        if ( token == 'int' or token == 'bool'):        #declarações
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
        
        if (token == 'break' or token == 'continue'):
            token = self.nextToken()
            
            if (token == ';'):
                return True
            else:
                self.salvarErro("Erro de desvio condicional")
                return False
        
        if (self.isId(token)):
            prox_token = self.listTokens[self.indice+1]  
            if (prox_token == '='):
                return self._atribuicao()
            return self._chamarFuncao()
            
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


analisador = analisadorSintatico()
analisador.inicio()