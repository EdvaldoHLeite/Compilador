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
from analisadorLexico import AnalisadorLexico

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
        self.listTokens, self.tokensLinhas = self.getListTokens()
        self.indice = 0


    def salvarErro(self, msg):
        self.arquivo_saida.writelines(msg + ", linha: "+str(int(self.tokensLinhas[self.indice])) + ", token>>"+self.listTokens[self.indice] + '\n')

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
                    self.salvarErro("Erro de expressão aritmética")
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
        self.salvarErro("Erro de expressão booleana")
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
        self.salvarErro("Erro de lista de parametros")
        return False

    #declaração de funções
    def _funcao(self):
        token = self.nextToken()
        if(self.listaParametros()):
            token = self.nextToken()
            if (token == '{'):
                token = self.nextToken()
                if(token != 'return' and token != '}'):
                    while(self._s()):
                        token = self.nextToken()
                        if (token == '}'):
                            break;
                    #token = self.nextToken()

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
        self.salvarErro("Erro de função")
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
        self.salvarErro("Erro de declaração")
        return False

    #print
    def _print(self):
        token = self.nextToken()
        if (token == 'id' or token == 'numero'):
            token = self.nextToken()
            if(token == ';'):
                return True
        self.salvarErro("Erro no print")
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
            if (self.listaParametros()):
                token = self.nextToken()
                if (token == ')'):
                    token = self.nextToken()
                    if (token == ';'):
                        return True
                if (token == ';'): #lista de parametros vazi entao o proxim eh o fim do comando
                    return True
        self.salvarErro("Erro na chamada de função")
        return False

    def _atribuicao(self):
        token = self.nextToken()
        if (token == '='):
            token = self.nextToken()
            if (token == 'id' or token == 'numero' or token == 'true' or token == 'false'):
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
        
        if (token == 'id'):
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
                    break
                self.nextToken()
            else:
                print ('SUCESSO na analise!\n')
                break
    
        self.arquivo_entrada.close()
        self.arquivo_saida.close()  

lexico = AnalisadorLexico()
lexico.analisar()
analisador = analisadorSintatico()
analisador.inicio()