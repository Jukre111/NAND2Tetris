import os
import sys
import nltk


KEYWORDS = ['class','constructor','function','method','field',
            'static','var','int','char','boolean','void','true',
            'false','null','this','let','do','if','else','while','return']

SYMBOLS = ['{','}','(',')','[',']','.',',',';','+','-','*','/','&','|','<','>','=','~']


STATEMENTS = ["let","if","while","do","return"]



def readFile(): #reads file and removes comments and empty lines
    list = []
    comment = 0
    with open(sys.argv[1],"r") as f:
        for line in f:
            if not line.startswith("//") and not line == '\n' and not line.isspace():
                if line.find("//")!=-1:
                    a = line.find("//")
                    if line[:a-1].find('.')!=-1:
                        for i in line[:a-1].split('.'):
                            list.append(i)
                            list.append(" . ")
                        list.pop()
                    elif line[:a-1].find('~')!=-1:
                        for i in line[:a-1].split('~'):
                            list.append(i)
                            list.append(" ~ ")
                        list.pop()
                    elif line[:a-1].find('-')!=-1:
                        for i in line[:a-1].split('-'):
                            list.append(i)
                            list.append(" - ")
                        list.pop()
                    else:
                        list.append(line[:a-1])
                elif comment==0 and line.find("/*")!=-1:
                    comment=1
                    if line.find("*/")!=-1:
                        comment=0
                elif comment==1 and line.find("*")!=-1 :
                    comment=1
                elif line.find("*/")!=-1 and comment==1:
                    comment = 0
                elif line.find('.')!=-1:
                    for i in line.split('.'):
                        list.append(i)
                        list.append(" . ")
                    list.pop()
                elif line.find('~')!=-1:
                    for i in line.split('~'):
                        list.append(i)
                        list.append(" ~ ")
                    list.pop()
                elif line.find('-')!=-1:
                    for i in line.split('-'):
                        list.append(i)
                        list.append(" - ")
                    list.pop()
                else:
                    list.append(line)
    f.close()
    return list


def tokenizer(): # calls readFile and proceeds to tokenize and save it as the list "tokens"
    tokens = []
    if len(sys.argv)>0:
        list = readFile()
        with open("tmp.xml","w+") as tmp:
            for line in list:
                tmp.write(line)
        tmp.close()
        with open("tmp.xml","r+") as tmp:
            tokens = nltk.word_tokenize(tmp.read())

        tmp.close()
        os.remove("tmp.xml")
        file = open(sys.argv[1][:-5]+"T.xml","w+")
        file.write("<tokens>\n")
        stringconstant = 0
        specialsymbols = {"<": "&lt;",">": "&gt;","&": "&amp;"}
        for i in tokens:
            if stringconstant==0 and i in KEYWORDS:
                file.write("<keyword> "+i+" </keyword>\n")
            elif stringconstant==0 and i in SYMBOLS:
                if i in specialsymbols:
                    file.write("<symbol> "+specialsymbols.get(i)+" </symbol>\n")
                else:
                    file.write("<symbol> "+i+" </symbol>\n")
            elif i == "``" or stringconstant==1:
                if i =="``" and stringconstant==0:
                    file.write("<stringConstant> ")
                    stringconstant=1
                elif i =="``" and stringconstant==1:
                    file.write(" </stringConstant>\n")
                    stringconstant=0
                elif i =="''" and stringconstant==1:
                    file.write(" </stringConstant>\n")
                    stringconstant=0
                else:
                    file.write(" "+i)
            elif i.isdigit():
                file.write("<integerConstant> "+i+" </integerConstant>\n")
            else:
                file.write("<identifier> "+i+" </identifier>\n")
        file.write("</tokens>")
    tokens = [specialsymbols.get(x) if x in specialsymbols else x for x in tokens]

    return tokens

def parser(tokenized):
    tokens = tokenized
    pos = 3
    with open(sys.argv[1][:-5]+".xml","w+") as file:
        file.write("<class>\n")
        file.write("<keyword> "+tokens[0]+" </keyword>\n")
        file.write("<identifier> "+tokens[1]+" </identifier>\n")
        file.write("<symbol> "+tokens[2]+" </symbol>\n")
        pos = parseStatement(tokens,pos,file)
        file.write("<symbol> "+tokens[pos]+" </symbol>\n")
        file.write("</class>")
    file.close()


def parseStatement(tokens,pos,file):
    while tokens[pos] in ["static","field"]:
        pos = classVarDec(tokens,pos,file)
    while tokens[pos] in ["constructor","function","method"]:
        pos = subroutineDec(tokens,pos,file)

    return pos

def classVarDec(tokens,pos,file):
    file.write("<classVarDec>\n")
    file.write("<keyword> " + tokens[pos] + " </keyword>\n")
    pos+=1
    if tokens[pos] in ["int","boolean","char"]:
        file.write("<keyword> " + tokens[pos] + " </keyword>\n")
    else:
        file.write("<identifier> " + tokens[pos] + " </identifier>\n")
    pos+=1
    file.write("<identifier> " + tokens[pos] + " </identifier>\n")
    while tokens[pos+1]!=";":
        pos+=1
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
        file.write("<identifier> " + tokens[pos] + " </identifier>\n")
    pos+=1
    file.write("<symbol> " + tokens[pos] + " </symbol>\n")
    file.write("</classVarDec>\n")
    pos+=1
    return pos

def subroutineDec(tokens,pos,file):
    file.write("<subroutineDec>\n")
    file.write("<keyword> " + tokens[pos] + " </keyword>\n")
    pos+=1
    if tokens[pos] in ["int","boolean","char","void"]:
        file.write("<keyword> " + tokens[pos] + " </keyword>\n")
    else:
        file.write("<identifier> " + tokens[pos] + " </identifier>\n")
    pos+=1
    file.write("<identifier> " + tokens[pos] + " </identifier>\n")
    pos+=1
    file.write("<symbol> " + tokens[pos] + " </symbol>\n")
    pos+=1
    file.write("<parameterList>\n")
    pos = parameterList(tokens,pos,file)
    file.write("</parameterList>\n")
    file.write("<symbol> " + tokens[pos] + " </symbol>\n")
    pos+=1

    pos = subroutineBody(tokens,pos,file)



    file.write("</subroutineDec>\n")
    return pos

def subroutineBody(tokens,pos,file):
    file.write("<subroutineBody>\n")
    file.write("<symbol> " + tokens[pos] + " </symbol>\n")
    pos+=1
    while tokens[pos]=="var":
        pos = varDec(tokens,pos,file)

    pos = statements(tokens,pos,file)
    file.write("<symbol> " + tokens[pos] + " </symbol>\n")
    file.write("</subroutineBody>\n")
    pos+=1
    return pos


def statements(tokens,pos,file):
    file.write("<statements>\n")
    while tokens[pos] in STATEMENTS:
        current = STATEMENTS.index(tokens[pos])
        if current==0:
            pos = letStatement(tokens,pos,file)
        elif current==1:
            pos = ifStatement(tokens,pos,file)
        elif current==2:
            pos = whileStatement(tokens,pos,file)
        elif current==3:
            pos = doStatement(tokens,pos,file)
        elif current==4:
            pos = returnStatement(tokens,pos,file)
    file.write("</statements>\n")
    if tokens[pos+1]=="else":
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
        file.write("<keyword> " + tokens[pos] + " </keyword>\n")
        pos+=1
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
        pos=statements(tokens,pos,file)
    return pos


def letStatement(tokens,pos,file):
    file.write("<letStatement>\n")
    file.write("<keyword> " + tokens[pos] + " </keyword>\n")
    pos+=1
    file.write("<identifier> " + tokens[pos] + " </identifier>\n")
    pos+=1
    file.write("<symbol> " + tokens[pos] + " </symbol>\n")
    pos+=1
    pos = expression(tokens,pos,file,1,0)
    if tokens[pos]=="=":
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
        pos = expression(tokens,pos,file,1,0)
    file.write("</letStatement>\n")
    return pos

def expressionList(tokens,pos,file,ifstat):
    file.write("<expressionList>\n")
    if tokens[pos]==")":
        file.write("</expressionList>\n")
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
        return pos
    else:
        pos = expression(tokens,pos,file,0,1)
    while tokens[pos]==",":
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
        pos = expression(tokens,pos,file,0,1)
    file.write("</expressionList>\n")
    file.write("<symbol> " + tokens[pos] + " </symbol>\n")
    pos+=1
    return pos

def expression(tokens,pos,file,list,ifstat):
    file.write("<expression>\n")
    pos = term(tokens,pos,file,ifstat)
    if (tokens[pos]=="*" and tokens[pos+1]=="(")  or (tokens[pos]=="/" and tokens[pos+1]=="("):
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
        pos = term(tokens,pos,file,1)
    if tokens[pos]=="/" or tokens[pos]=="|" or tokens[pos]=="=":
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
        pos = term(tokens,pos,file,ifstat)
    file.write("</expression>\n")
    if list!=0:
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
    return pos

def term(tokens,pos,file,ifstat):
    file.write("<term>\n")
    if tokens[pos].isdigit():
        file.write("<integerConstant> " + tokens[pos] + " </integerConstant>\n")
        pos+=1
    elif tokens[pos].startswith('``'):
        fullstring = ""
        pos+=1
        while not (tokens[pos+1].startswith('``') or tokens[pos+1].startswith("''")):
            fullstring+=" "+tokens[pos]
            pos+=1
        fullstring+=tokens[pos]
        file.write("<stringConstant> " + fullstring + " </stringConstant>\n")
        pos+=1
        pos+=1
    elif tokens[pos]=="-":
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
        pos = term(tokens,pos,file,0)
    elif tokens[pos]=="~":
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
        pos = term(tokens,pos,file,1)
    elif tokens[pos] in ["true", "false", "null", "this"]:
        file.write("<keyword> " + tokens[pos] + " </keyword>\n")
        pos+=1
    elif tokens[pos]=="(":
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
        if tokens[pos]=="(" or ifstat==1:
            file.write("<expression>\n")
            while tokens[pos]!=")":
                pos = term(tokens,pos,file,1)
                if tokens[pos]!=")":
                    file.write("<symbol> " + tokens[pos] + " </symbol>\n")
                else:
                    file.write("</expression>\n")
                    file.write("<symbol> " + tokens[pos] + " </symbol>\n")
                    break
                pos+=1
            pos+=1
        else:
            ifstat = 1
            pos = expressionList(tokens,pos,file,ifstat)
            file.write("<symbol> " + tokens[pos] + " </symbol>\n")
            pos+=1
    elif tokens[pos+1]=="[":
        file.write("<identifier> " + tokens[pos] + " </identifier>\n")
        pos+=1
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
        pos = expression(tokens,pos,file,0,0)
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
    elif tokens[pos+1]==".":
        file.write("<identifier> " + tokens[pos] + " </identifier>\n")
        pos+=1
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
        file.write("<identifier> " + tokens[pos] + " </identifier>\n")
        pos+=1
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
        pos = expressionList(tokens,pos,file,0)
    else:
        file.write("<identifier> " + tokens[pos] + " </identifier>\n")
        pos+=1

    file.write("</term>\n")
    if tokens[pos]=="+" or tokens[pos]=="-" or tokens[pos] in ["&lt;","&gt;","&amp;"]:
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
        pos = term(tokens,pos,file,0)

    return pos


def ifStatement(tokens,pos,file):
    file.write("<ifStatement>\n")
    file.write("<keyword> " + tokens[pos] + " </keyword>\n")
    pos+=1
    file.write("<symbol> " + tokens[pos] + " </symbol>\n")
    pos+=1
    pos = expression(tokens,pos,file,1,1)
    file.write("<symbol> " + tokens[pos] + " </symbol>\n")
    pos+=1
    pos = statements(tokens,pos,file)
    file.write("<symbol> " + tokens[pos] + " </symbol>\n")
    pos+=1
    file.write("</ifStatement>\n")
    return pos

def whileStatement(tokens,pos,file):
    file.write("<whileStatement>\n")
    file.write("<keyword> " + tokens[pos] + " </keyword>\n")
    pos+=1
    file.write("<symbol> " + tokens[pos] + " </symbol>\n")
    pos+=1
    pos = expression(tokens,pos,file,1,1)
    file.write("<symbol> " + tokens[pos] + " </symbol>\n")
    pos+=1
    pos = statements(tokens,pos,file)
    file.write("<symbol> " + tokens[pos] + " </symbol>\n")
    pos+=1
    file.write("</whileStatement>\n")
    return pos

def doStatement(tokens,pos,file):
    file.write("<doStatement>\n")
    file.write("<keyword> " + tokens[pos] + " </keyword>\n")
    pos+=1
    file.write("<identifier> " + tokens[pos] + " </identifier>\n")
    pos+=1
    if tokens[pos]==".":
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
        file.write("<identifier> " + tokens[pos] + " </identifier>\n")
        pos+=1
    file.write("<symbol> " + tokens[pos] + " </symbol>\n")
    pos+=1
    pos = expressionList(tokens,pos,file,0)
    file.write("<symbol> " + tokens[pos] + " </symbol>\n")
    pos+=1
    file.write("</doStatement>\n")
    return pos

def returnStatement(tokens,pos,file):
    file.write("<returnStatement>\n")
    file.write("<keyword> " + tokens[pos] + " </keyword>\n")
    pos+=1
    if tokens[pos]!=";":
        pos = expression(tokens,pos,file,1,0)
    else:
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
    file.write("</returnStatement>\n")
    return pos





def parameterList(tokens,pos,file):
    if tokens[pos] in ["int","boolean","char"]:
        file.write("<keyword> " + tokens[pos] + " </keyword>\n")
    elif tokens[pos]==")":
        return pos
    else:
        file.write("<identifier> " + tokens[pos] + " </identifier>\n")
    pos+=1
    file.write("<identifier> " + tokens[pos] + " </identifier>\n")
    pos+=1
    while tokens[pos]==",":
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
        if tokens[pos] in ["int","boolean","char"]:
            file.write("<keyword> " + tokens[pos] + " </keyword>\n")
        else:
            file.write("<identifier> " + tokens[pos] + " </identifier>\n")
        pos+=1
        file.write("<identifier> " + tokens[pos] + " </identifier>\n")
        pos+=1
    return pos

def varDec(tokens,pos,file):
    file.write("<varDec>\n")
    file.write("<keyword> " + tokens[pos] + " </keyword>\n")
    pos+=1
    if tokens[pos] in ["int","boolean","char"]:
        file.write("<keyword> " + tokens[pos] + " </keyword>\n")
    else:
        file.write("<identifier> " + tokens[pos] + " </identifier>\n")
    pos+=1
    file.write("<identifier> " + tokens[pos] + " </identifier>\n")
    while tokens[pos+1]!=";":
        pos+=1
        file.write("<symbol> " + tokens[pos] + " </symbol>\n")
        pos+=1
        file.write("<identifier> " + tokens[pos] + " </identifier>\n")
    pos+=1
    file.write("<symbol> " + tokens[pos] + " </symbol>\n")
    file.write("</varDec>\n")
    pos+=1
    return pos








############calls
tokenized = tokenizer()
parser(tokenized)
