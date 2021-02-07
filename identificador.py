class identificador(): 
    contexto = 0
    valor = ""
    tipo = ""                          
    funcao = False

    def __init__(self, lexema, num):    #num é o numero do identificador. Ex.: para id2, num = 2
        self.lexema = lexema
        self.id = "id"+str(num)

    def toString(self):
        return "token = "+self.id+"\nlexema = "+self.lexema+"\ntipo = "+self.tipo+"\nvalor = "+self.valor+"\ncontexto = "+str(self.contexto)+"\nfunção"+str(self.funcao)