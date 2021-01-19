'''
LISTA DE TOKENS

(DELIMITADORES)
aParentese
fParenteses
aChaves
fChaves
pontoVirgula
virgula

(OPERADOR)
operador
atribuicao

(IDENTIFICADOR)
id

(DIGITO)
numero

(RESERVADAS)
if
else
ifelse
while
break
continue
return
true
false
bool
int
'''

import os.path
import string

#criar a pilha
#iniciar o primeiro elemento da pilha com $

#"criar a tabela" (talvez não seja necessário)
#Cada estado define se o analisador vai empilhar o proximo token ou reduzir a produção
#cada estado é uma função
#ao final da analiza, a pilha deve estar vazia (apenas o simbolo $)

class analisadorSintatico():
    def __init__(self):
        self.arquivo_entrada = open("tokens_teste", 'r')
        self.arquivo_saida = open("saida_sintatico", 'w')
        self.listTokens = self.getListTokens()
        self.indice = 0




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

        for i in tokens:
            listTokens.append(self.getToken(i))
        listTokens.append('$')

        return listTokens

    def nextToken(self):    #incrementa o indice e retorna o proximo token de listToken
        self.indice += 1
        return self.listTokens[self.indice]

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
        parenteses = False

        if (token == '('):
            token = self.nextToken()
            parenteses == True

        if (token == 'id' or token == 'numero'):

            token = self.nextToken()

            if (self.operadorArit()):
                token = self.nextToken()
                if (token == 'id' or token == 'numero'):
                    token = self.nextToken()
                    if (parenteses == True):
                        if (token == ')'):
                            token = self.nextToken()
                    if (self.operadorArit()):
                        self.expressaoArit(self.nextToken())
                    else:
                        return True
                else:
                    return False    #caso a espressao esteja incompleta
            else:
                return True #caso a expressão seja apenas Id


    #expressoes boleanas
    def expressaoBool(self):
        token = self.nextToken()
        if(self.expressaoArit() or token == 'true' or token == 'false'):
            token = self.listTokens[self.indice]

            if(self.operadorBool()):
                token = self.nextToken()
                if(self.expressaoArit() or token == 'true' or token == 'false'):
                    return True
        return False

    #lista de parametros
    def listaParametros(self):
        token = self.listTokens[self.indice]

        if (token == 'int' or token == 'bool'):
            token = self.nextToken()
            if(token == 'id'):
                token = self.nextToken()
                if (token == ';'):
                    token = self.nextToken()
                    if (token == 'int' or 'bool'):  #é verificado novamente para não ser possivel colocar algo do tipo (.... int a;)
                        return self.listaParametros()
                elif(token == ')'):
                    return True
        elif(token == ')'):         #lista de parametros vazia
            return True
        return False

    #declaração de funções
    def _funcao(self):
        token = self.nextToken()
        if(self.listaParametros()):
            token = self.nextToken()
            if (token == '{'):
                token = self.nextToken()
                if(token != 'return' and token != '}'):
                    self._s()
                    token = self.nextToken()

                if(token == '}'):
                    return True

                if  (token == 'return'):
                    token = self.nextToken()
                    if(token == 'id' or token == 'true' or token == 'false' or token == 'numero'):
                        token = self.nextToken()
                        if (token == ';'):
                            token = self.nextToken()
                            if(token == '}'):
                                return True 
                elif(token == '}'): 
                    return True
        return False


    #declaração de variaveis e funções
    def _declaracao(self):
        token = self.nextToken()
        if (token == 'id'):
            token = self.nextToken()

            if (token == '('):               #se for uma função
                return self._funcao()        #retornará True caso o sintaxe da função esteja correta
            elif (token == '='):             #se for a atribuição de uma variavel
                token = self.nextToken()
                if (token == 'numero' or token == 'true' or token == 'false'):
                    token = self.nextToken()
                    if (token == ';'):
                        return True
            elif(token == ';'):               #se for uma declaração de variavel, sem atribuição
                return True
        return False

    #print
    def _print(self):
        token = self.nextToken()
        if (token == 'id' or token == 'numero'):
            token = self.nextToken()
            if(token == ';'):
                return True
        return False

    #if
    def _if(self):
        token = self.nextToken()

        if (token == '('):
            if (self.expressaoBool()):
                token = self.listTokens[self.indice]
                if (token == ')'):
                    token = self.nextToken()
                    if (token == '{'):
                        token = self.nextToken()
                        if (self._s()):
                            token = self.nextToken()
                            if (token == '}'):
                                return True
        return False

    def _s(self):
        token = self.listTokens[self.indice]
        if ( token == 'int' or token == 'bool'):        #declarações
            if (self._declaracao() == True):
                return True
            return False
        if (token == 'print'):
            return self._print()
        
        if (token == 'if'):
            return self._if()
        
        return False
            

    def inicio(self):
        while (True):
            if (self.indice < len(self.listTokens) -1):
                if (self._s() == False): #chamar a função inicial, que irá percorrer os tokens recursivamente
                    print ('ERRO na analise!\n') 
                    break
                self.nextToken()
            else:
                print ('SUCESSO na analise!\n')
                break
    
        self.arquivo_entrada.close()
        self.arquivo_saida.close()  

analisador = analisadorSintatico()
analisador.inicio()