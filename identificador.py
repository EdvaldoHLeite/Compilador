class identificador(): 
    contexto = 0
    valor = ""
    tipo = ""                           #função, int, bool, procedimento

    def __init__(self, lexema, num):    #num é o numero do identificador. Ex.: para id2, num = 2
        self.lexema = lexema
        self.id = "id"+str(num)