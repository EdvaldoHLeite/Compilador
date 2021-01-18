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

    #lista de parametros
    def listaParametros(self):
        token = self.listTokens[indice]

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
                self._s()
                token = self.nextToken()
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

            if (token == '('):
                return self._funcao()        #retornará True caso o sintaxe da função esteja correta
            elif (token == '='):
                token = self.nextToken()

                if (token == 'numero' or token == 'true' or token == 'false'):
                    token = self.nextToken()
                    if (token == ';'):
                        return True
        
        return False

    #print
    def _print(self):
        token = self.nextToken
        if (token == 'id' or token == 'numero'):
            token = self.nextToken()
            if(token == ';'):
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
        return False
            

    def inicio(self):
        if (self._s() == True): #chamar a função inicial, que irá percorrer os tokens recursivamente
            print ('SUCESSO na analise!\n')
        else:
            print ('ERRO na analise!\n') 
    
        self.arquivo_entrada.close()
        self.arquivo_saida.close()  

analisador = analisadorSintatico()
analisador.inicio()