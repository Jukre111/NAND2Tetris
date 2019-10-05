from  tkinter import *
from tkinter import filedialog
import os
import random
import string

commands = {
    "add": "M=M+D",
    "sub": "M=M-D",
    "neg": "M=-M",
    "and": "M=M&D",
    "or" : "M=M|D",
    "not": "M=!M"
}


class Application(Frame):
    fileName = ""
    path = ""
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()

    def init_window(self):
        self.master.title("VM Compiler")
        self.pack(fill=BOTH,expand=1)
        openFileBtn = Button(self,text="Choose Vm File",command=self.chooseFile)
        exitBtn = Button(self,text="Quit",command=self.exit_frame)
        openFileBtn.place(x=150,y=50)
        exitBtn.place(x=300,y=50)

    def exit_frame(self):
        exit()

    def chooseFile(self):
        content = []
        asm = []
        self.filename = filedialog.askopenfilename(initialdir = "E:/",title = "Choose your .vm file",filetypes = (("vm Files","*.vm"),("all files","*.*")))
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
            textmsg = "Succsessfully created \n"+fileName+".asm in \n"+path
            fileMessage = Label(self, text=textmsg)
            fileMessage.place(x=20,y=150)
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



root = Tk()

#size of the window
root.geometry("500x500")

app = Application(root)
root.mainloop()
