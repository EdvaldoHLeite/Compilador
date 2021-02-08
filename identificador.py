class identificador(): 
    def __init__(self, lexema, num):    #num é o numero do identificador. Ex.: para id2, num = 2
        self.lexema = lexema
        self.id = "id"+str(num)
        self.contexto = 0
        self.valor = ""
        self.tipo = ""                          
        self.funcao = False
        self.parametros = list()                 #lista de parametros da função ou do procedimento

    def toString(self):
        return "token = "+self.id+"\nlexema = "+self.lexema+"\ntipo = "+self.tipo+"\nvalor = "+self.valor+"\ncontexto = "+str(self.contexto)+"\nfunção = "+str(self.funcao)