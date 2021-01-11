# -*- coding: utf-8 -*-

import os.path
import string
import re

"""
identificador_
numero_
palavraReservada_:
    "int bool true false return if ifelse else while break continue"
delimitador_:
    "(){};,"
operador_:
    "+ - / * == != > >= < <= ="
    
Obs.: acompanhados de _linha
"""

class AnalisadorLexico():
    def __init__(self):
        self.entrada = "teste"
        self.saida = "tokens_teste"
        
    def setEntrada(self, nome_entrada):
        self.entrada = nome_entrada
        self.saida = "tokens_" + self.entrada
    
    def ehDelimitador(self, entrada):
        delimitadores = "(){};,"
        if entrada in delimitadores:
            return True
        return False
    
    # identifica se a entrada eh uma palavra reservada
    def ehReservada(self, entrada):
        reservadas = "int bool true false return if ifelse else while break continue"
        if entrada in reservadas.split():
            return True
        return False
    
    def ehOperador(self, entrada):
        operadores = "+ - / * == != > >= < <= = !"
        if entrada in operadores.split():
            return True
        return False
    
    def ehDigito(self, entrada):
        digitos = "0123456789"
        if entrada in digitos:
            return True
        return False
    
    def ehLetra(self, entrada):
        letras = re.compile('[a-zA-Z]')
        return letras.search(entrada)
        
    def analisar(self):
        arquivo_entrada = open(self.entrada, 'r')
        arquivo_saida = open(self.saida, 'w')
        
        linha = True
        numero_linha = 0
        
        # percorre linha por linha
        while linha:
            linha = arquivo_entrada.readline()
            #linha = linha.replace(" ", "") 
            #linha.replace("\n", "")
            numero_linha += 1
            tamanho_linha = len(linha)            
            
            i_car = 0 # percorre os caracteres da linha
            while i_car < tamanho_linha:
                caractere_atual = linha[i_car]
                caractere_seguinte = None
                if (i_car+1 < tamanho_linha):
                    caractere_seguinte = linha[i_car+1]
                    
                #### delimitador ####
                if self.ehDelimitador(caractere_atual):
                    if  ('('):
                        arquivo_saida.write("aParenteses_"+caractere_atual+"_"+str(numero_linha)+"\n")
                    elif(')'):
                        arquivo_saida.write("fParenteses_"+caractere_atual+"_"+str(numero_linha)+"\n")
                    elif('{'):
                        arquivo_saida.write("aChaves"+caractere_atual+"_"+str(numero_linha)+"\n")
                    elif('}'):
                        arquivo_saida.write("fChaves"+caractere_atual+"_"+str(numero_linha)+"\n")
                    elif(';'):
                        arquivo_saida.write("pontoVirgula"+caractere_atual+"_"+str(numero_linha)+"\n")
                    elif(','):
                        arquivo_saida.write("virgula_"+caractere_atual+"_"+str(numero_linha)+"\n")

                
                #### operador ####
                elif self.ehOperador(caractere_atual):
                    operador = caractere_atual
                    if caractere_seguinte != None and self.ehOperador(caractere_atual+caractere_seguinte): # operador com dois caracteres como '=='
                        i_car += 1 # o operador tem dois sinais
                        operador = caractere_atual + caractere_seguinte
                    arquivo_saida.write("operador_"+operador+"_"+str(numero_linha)+"\n")
                
                
                ### numero ###
                elif self.ehDigito(caractere_atual):
                    numero = caractere_atual # armazena o numero
                    
                    i_seguinte = i_car + 1 # contem o indice dos proximos caracteres
                    prox_car = linha[i_car+1]
                    while self.ehDigito(prox_car): # percorre a linha enquanto houver digitos
                        numero += prox_car
                        
                        if i_seguinte < tamanho_linha:
                            i_seguinte += 1
                            prox_car = linha[i_seguinte]
                        else:
                            break
                            
                    i_car = i_seguinte -1 # atualiza o indice do caractere atual
                    arquivo_saida.write("numero_"+numero+"_"+str(numero_linha)+'\n')
                
                
                #### palavras reservadas e identificadores ####
                elif self.ehLetra(caractere_atual):
                    texto = caractere_atual
                    
                    i_prox = i_car+1
                    while i_prox < tamanho_linha and linha[i_prox] != " " and linha[i_prox] != "\n": # busca de letras ou digitos, encerra quando chega no final da linha ou encontra qualquer outro tipo de caractere
                        
                        prox = linha[i_prox]
                        if self.ehLetra(prox) or self.ehDigito(prox):
                            texto += prox
                            i_prox += 1
                        else:
                            break

                    if self.ehReservada(texto):
                        if  (texto == "if"):
                            arquivo_saida.write("if_"+texto+"_"+str(numero_linha)+'\n')
                        elif(texto == "else"):
                            arquivo_saida.write("else_"+texto+"_"+str(numero_linha)+'\n')
                        elif(texto == "ifelse"):
                            arquivo_saida.write("ifelse_"+texto+"_"+str(numero_linha)+'\n')
                        elif(texto == "while"):
                            arquivo_saida.write("while_"+texto+"_"+str(numero_linha)+'\n')
                        elif(texto == "break"):
                            arquivo_saida.write("brak_"+texto+"_"+str(numero_linha)+'\n')
                        elif(texto == "continue"):
                            arquivo_saida.write("continue_"+texto+"_"+str(numero_linha)+'\n')
                        elif(texto == "return"):
                            arquivo_saida.write("return_"+texto+"_"+str(numero_linha)+'\n')
                        elif(texto == "true"):
                            arquivo_saida.write("true_"+texto+"_"+str(numero_linha)+'\n')
                        elif(texto == "false"):
                            arquivo_saida.write("false_"+texto+"_"+str(numero_linha)+'\n')
                        elif(texto == "bool"):
                            arquivo_saida.write("bool_"+texto+"_"+str(numero_linha)+'\n')
                        elif(texto == "int"):
                            arquivo_saida.write("int_"+texto+"_"+str(numero_linha)+'\n')
                    else:
                        arquivo_saida.write("id_"+texto+"_"+str(numero_linha)+'\n')
                    i_car = i_prox -1

                i_car += 1
        
        arquivo_saida.write("fim")
        arquivo_entrada.close()
        arquivo_saida.close()
    
lexico = AnalisadorLexico()
lexico.analisar()

# colocando uma id como "56aa", é erro de sintaxe ou lexico?
# no if acima se for tratado os ids antes de numeros, este erro não ocorre

                
                
        
        