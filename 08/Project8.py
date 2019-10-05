import os
import random
import string
import sys

commands = {
    "add": "M=M+D",
    "sub": "M=M-D",
    "neg": "M=-M",
    "and": "M=M&D",
    "or" : "M=M|D",
    "not": "M=!M"
}

counter = 1

class Application():
    fileName = ""
    path = ""

    def chooseFile(self):
        content = []
        asm = []
        self.filename = sys.argv[1]
        path =  os.path.split(self.filename)[0]+os.path.sep
        fileName = os.path.split(self.filename)[1].split(".vm")[0]
        if os.path.exists(path) and len(fileName)>0:
            content=open(path+fileName+".vm","r").readlines()
            asm = self.compile(content,fileName)
        if len(asm)!=0:
            self.createAndFillAsmFile(fileName,path,asm)

    def createAndFillAsmFile(self, fileName, path, asm):
        if os.path.exists(path) and len(fileName)>0:
            os.path.join(path, fileName+".asm")
            f = open(path+fileName+".asm", "w+")
            for x in range(len(asm)):
                f.write(asm[x]+"\n")
            f.close()

    def compile(self, content,fileName):
        actualLine = 0
        commands = []
        asmFile = ["@256","D=A","@SP","M=D"]
        for x in range(len(content)):
            content[x] = content[x].lstrip(' ')
            if content[x].startswith("//") or content[x] == '\n':  # comment
                actualLine-=1
                content[x]=""
            else:
                commands = content[x].split()
                for x in self.handleCommands(commands,fileName):
                    asmFile.append(x)
            actualLine+=1




        print(asmFile)
        return asmFile

    def handleCommands(self,command,fileName):
        label = ''.join(random.choice(string.ascii_uppercase) for i in range(10)) #random labelname, kann doppelt vorkommen ist aber egal, da aufgrund der syntax erst immer das andere label kommen sollte
        asm = []
        if command[0] in commands:  # kuemmert sich um die Commands: add, neg, sub, and, or, not
            if  command[0] == "neg" or command[0] == "not":
                for x in range(4,8):
                    asm.append(self.cleanStack()[x])
            else:
                for x in self.cleanStack():
                    asm.append(x)
            asm.append(commands.get(command[0])) # commando
            asm.append("@SP")
            asm.append("M=M+1")
        elif command[0] in ["eq","lt","gt"]: # wenn ein bool vorliegt
            for x in self.cleanStack():
                asm.append(x)
            asm.append("D=M-D") #  entweder negativ, positiv oder 0
            asm.append("@"+label)   # label gefolgt von jump
            asm.append({"eq":"D;JEQ","lt":"D;JLT","gt":"D;JGT"}.get(command[0]))
            asm.append("@SP")   # 3 zeilen => true
            asm.append("A=M")
            asm.append("M=0")
            asm.append("@"+label+"2") # 2 zeilen => label gefolgt von jump
            asm.append("0;JMP")
            asm.append("("+label+")")       # labelanfang
            asm.append("@SP")   # 3 zeilen => false
            asm.append("A=M")
            asm.append("M=-1")
            asm.append("("+label+"2)")  #endlabelanfang
            asm.append("@SP")
            asm.append("M=M+1")


        elif command[0] == "push":
            if command[1] == "constant":
                asm.append("@"+command[2])
                asm.append("D=A")
            else:
                for x in self.push_registers(command[2],command[1],fileName):
                    asm.append(x)
            for x in self.push():
                asm.append(x)
            asm.append("@SP")
            asm.append("M=M+1")
        elif command[0] == "pop":
            for x in self.pop_registers(command[2],command[1],fileName):
                asm.append(x)

        elif command[0] == "label":
            asm.append("("+fileName+"$"+command[1]+")")
        elif command[0] == "if-goto":
            asm.append("@SP")
            asm.append("M=M-1")
            asm.append("A=M")
            asm.append("D=M")
            asm.append("@"+fileName+"$"+command[1])
            asm.append("D;JNE")
        elif command[0] == "goto":
            asm.append("@"+fileName+"$"+command[1])
            asm.append("0;JMP")

        elif command[0] == "function":
            asm.append("("+command[1]+")")
            for i in command[2]:
                asm.append("D=0")
                asm.append("@SP")
                asm.append("A=M")
                asm.append("M=D")
                asm.append("@SP")
                asm.append("M=M+1")
        elif command[0] == "return":
            for x in self.return_func():
                    asm.append(x)

        elif command[0] == "call":
            global counter
            for x in self.call_func(command[2],command[1],fileName,counter):
                    asm.append(x)
            counter+=1

        return asm

    def return_func(self): #slide 20 als asm Uebersetzung
        asm = ["@LCL","D=M","@frame","M=D","@5","D=D-A","A=D","D=M","@retAddr","M=D","@SP","A=M-1","D=M","@ARG","A=M",
               "M=D","@ARG","D=M","@SP","M=D+1","@frame","AM=M-1","D=M","@THAT","M=D","@frame","AM=M-1","D=M","@THIS",
               "M=D","@frame","AM=M-1","D=M","@ARG","M=D","@frame","AM=M-1","D=M","@LCL","M=D","@retAddr","A=M","0;JMP"]
        return asm


    def call_func(self,arg,name,fileName,counter):
        asm = ["@call."+name+""+str(counter),"D=A","@SP","A=M","M=D","@SP","M=M+1","@LCL","D=M","@SP","A=M","M=D","@SP","M=M+1",
               "@ARG","D=M","@SP","A=M","M=D","@SP","M=M+1","@THIS","D=M","@SP","A=M","M=D","@SP","M=M+1",
               "@THAT","D=M","@SP","A=M","M=D","@SP","M=M+1","@SP","D=M","@ARGS","D=D-A","@5","D=D-A","@ARG","M=D",
               "@SP","D=M","@LCL","M=D","@"+name,"0;JMP","("+"call."+name+""+str(counter)+")"]
        return asm

    def push(self):
        asm = ["@SP","A=M","M=D"]
        return asm

    def cleanStack(self):
        asm = ["@SP","M=M-1","A=M","D=M","@SP","M=M-1","@SP","A=M"]
        return asm

    def push_registers(self,value,register,fileName):
        registers = {"this":"@THIS","that":"@THAT","argument":"@ARG","local":"@LCL"}
        if register in registers:
            asm = [registers.get(register),"D=M","@"+str(value),"A=D+A","D=M"]
        if register == "temp":
            asm = ["@R6","D=M"]
        if register == "pointer":
            asm = ["@R"+str(3+int(value)),"D=M"]
        if register == "static":
            asm = ["@"+str(fileName)+"."+str(value),"D=M"]
        return asm

    def pop_registers(self,value,register,fileName):
        registers = {"this":"@THIS","that":"@THAT","argument":"@ARG","local":"@LCL"}
        if register in registers:
            asm = [registers.get(register),"D=M","@"+str(value),"A=D+A","D=A","@R15","M=D","@SP","M=M-1","A=M","D=M","@R15","A=M","M=D"]
        if register == "temp":
            asm = ["@R6","D=A","@R15","M=D","@SP","M=M-1","A=M","D=M","@R15","A=M","M=D"]
        if register == "pointer":
            asm = ["@R"+str(3+int(value)),"D=A","@R15","M=D","@SP","M=M-1","A=M","D=M","@R15","A=M","M=D"]
        if register == "static":
            asm = ["@"+str(fileName)+"."+str(value),"D=A","@R15","M=D","@SP","M=M-1","A=M","D=M","@R15","A=M","M=D"]
        return asm





app = Application()

app.chooseFile()
