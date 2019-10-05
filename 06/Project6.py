from  tkinter import *
from tkinter import filedialog
import os

memory = 16

hash = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576,
    "R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4, "R5": 5, "R6": 6, "R7": 7, "R8": 8, "R9": 9, "R10": 10, "R11": 11, "R12": 12, "R13": 13, "R14": 14, "R15": 15
    }


class Application(Frame):
    fileName = ""
    path = ""
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()

    def init_window(self):
        self.master.title("Binary Compiler")
        self.pack(fill=BOTH,expand=1)
        openFileBtn = Button(self,text="Choose Asm File",command=self.chooseFile)
        exitBtn = Button(self,text="Quit",command=self.exit_frame)
        openFileBtn.place(x=100,y=50)
        exitBtn.place(x=250,y=50)

    def exit_frame(self):
        exit()

    def chooseFile(self):
        content = []
        hack = []
        self.filename = filedialog.askopenfilename(initialdir = "E:/",title = "Choose your .asm file",filetypes = (("Asm Files","*.asm"),("all files","*.*")))
        path =  os.path.split(self.filename)[0]+os.path.sep
        fileName = os.path.split(self.filename)[1].split(".asm")[0]
        if os.path.exists(path) and len(fileName)>0:
            content=open(path+fileName+".asm","r").readlines()
            hack = self.compile(content)
        if len(hack)!=0:
            self.createAndFillHackFile(fileName,path,hack)

    def createAndFillHackFile(self, fileName, path, hack):
        if os.path.exists(path) and len(fileName)>0:
            os.path.join(path, fileName+".hack")
            textmsg = "Succsessfully created \n"+fileName+".hack in \n"+path
            fileMessage = Label(self, text=textmsg)
            fileMessage.pack()
            f = open(path+fileName+".hack", "w+")
            for x in range(len(hack)):
                f.write(hack[x]+"\n")
            f.close()

    def compile(self, content):
        actualLine = 0
        for x in range(len(content)):
            content[x] = content[x].lstrip(' ')
            if content[x].startswith("//") or content[x] == '\n':  # comment
                actualLine-=1
            if content[x].startswith("("):
                hash[content[x][1:-2]] = int(actualLine)
                actualLine-=1
                content[x] = "//"
            actualLine+=1
        clean16Bit = ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0']
        saving16Bit = clean16Bit
        result16Bit = ""
        binarycode = []
        for x in range(len(content)):
            saving16Bit = clean16Bit.copy()
            if content[x].startswith("@"): # a-Instruction
                if content[x][1].isalpha():
                    value = hash.get(content[x][1:-1])
                    if value == None:
                        global memory
                        hash[content[x][1:-1]] = memory
                        memory+=1
                        value = hash.get(content[x][1:-1])
                    binarycode.append(bin(value)[2:].zfill(16))
                else:
                    binarycode.append(bin(int(content[x][1:]))[2:].zfill(16))
            elif content[x].startswith("//") or content[x]=='\n': # comment
                pass
            else: # c-Instruction
                saving16Bit[0], saving16Bit[1], saving16Bit[2] = '1','1','1'
                # jump
                jumpBool = 0
                if ";JMP" in content[x]:
                    saving16Bit[13], saving16Bit[14], saving16Bit[15] = '1', '1', '1'
                    jumpBool=1
                elif ";JLT" in content[x]:
                    saving16Bit[13], saving16Bit[14], saving16Bit[15] = '1', '0', '0'
                    jumpBool=1
                elif ";JGT" in content[x]:
                    saving16Bit[13], saving16Bit[14], saving16Bit[15] = '0', '0', '1'
                    jumpBool=1
                elif ";JEQ" in content[x]:
                    saving16Bit[13], saving16Bit[14], saving16Bit[15] = '0', '1', '0'
                    jumpBool=1
                elif ";JGE" in content[x]:
                    saving16Bit[13], saving16Bit[14], saving16Bit[15] = '0', '1', '1'
                    jumpBool=1
                elif ";JNE" in content[x]:
                    saving16Bit[13], saving16Bit[14], saving16Bit[15] = '1', '0', '1'
                    jumpBool=1
                elif ";JLE" in content[x]:
                    saving16Bit[13], saving16Bit[14], saving16Bit[15] = '1', '1', '0'
                    jumpBool=1

                #comp
                if jumpBool==0:
                    # dest
                    if content[x].startswith("MD"):
                        saving16Bit[10], saving16Bit[11], saving16Bit[12] = '0', '1', '1'
                    elif content[x].startswith("M"):
                        saving16Bit[10], saving16Bit[11], saving16Bit[12] = '0', '0', '1'
                    elif content[x].startswith("D"):
                        saving16Bit[10], saving16Bit[11], saving16Bit[12] = '1', '0', '0'
                    elif content[x].startswith("AMD"):
                        saving16Bit[10], saving16Bit[11], saving16Bit[12] = '1', '1', '1'
                    elif content[x].startswith("AM"):
                        saving16Bit[10], saving16Bit[11], saving16Bit[12] = '0', '1', '0'
                    elif content[x].startswith("AD"):
                        saving16Bit[10], saving16Bit[11], saving16Bit[12] = '1', '1', '0'
                    elif content[x].startswith("A"):
                        saving16Bit[10], saving16Bit[11], saving16Bit[12] = '1', '0', '1'

                    if "=0" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','1','0','1','0','1','0'
                    elif "=1" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','1','1','1','1','1','1'
                    elif "=-1" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','1','1','1','0','1','0'
                    elif "=D+M" in content[x]:
                        saving16Bit[3], saving16Bit[4], saving16Bit[5], saving16Bit[6], saving16Bit[7], saving16Bit[8], saving16Bit[9] = '1', '0', '0', '0', '0', '1', '0'
                    elif "=D-M" in content[x]:
                        saving16Bit[3], saving16Bit[4], saving16Bit[5], saving16Bit[6], saving16Bit[7], saving16Bit[8], saving16Bit[9] = '1', '0', '1', '0', '0', '1', '1'
                    elif "=M-D" in content[x]:
                        saving16Bit[3], saving16Bit[4], saving16Bit[5], saving16Bit[6], saving16Bit[7], saving16Bit[8], saving16Bit[9] = '1', '0', '0', '0', '1', '1', '1'
                    elif "=D&M" in content[x]:
                        saving16Bit[3], saving16Bit[4], saving16Bit[5], saving16Bit[6], saving16Bit[7], saving16Bit[8], saving16Bit[9] = '1', '0', '0', '0', '0', '0', '0'
                    elif "=D|M" in content[x]:
                        saving16Bit[3], saving16Bit[4], saving16Bit[5], saving16Bit[6], saving16Bit[7], saving16Bit[8], saving16Bit[9] = '1', '0', '1', '0', '1', '0', '1'
                    elif "=D+1" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','0','1','1','1','1','1'
                    elif "=D-1" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','0','0','1','1','1','0'
                    elif "=D+A" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','0','0','0','0','1','0'
                    elif "=D-A" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','0','1','0','0','1','1'
                    elif "=D&A" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','0','0','0','0','0','0'
                    elif "=D|A" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','0','1','0','1','0','1'
                    elif "=D" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','0','0','1','1','0','0'
                    elif "=-A" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','1','1','0','0','1','1'
                    elif "=A+1" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','1','1','0','1','1','1'
                    elif "=A-1" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','1','1','0','0','1','0'
                    elif "=A-D" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','0','0','0','1','1','1'
                    elif "=A" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','1','1','0','0','0','0'
                    elif "=!D" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','0','0','1','1','0','1'
                    elif "=!A" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','1','1','0','0','0','1'
                    elif "=-D" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','0','0','1','1','1','1'
                    elif "=!M" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '1','1','1','0','0','0','1'
                    elif "=-M" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '1','1','1','0','0','1','1'
                    elif "=M+1" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '1','1','1','0','1','1','1'
                    elif "=M-1" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '1','1','1','0','0','1','0'
                    elif "=M" in content[x]:
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '1','1','1','0','0','0','0'
                else:
                    if content[x].startswith("0"):
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','1','0','1','0','1','0'
                    elif content[x].startswith("D"):
                        saving16Bit[3],saving16Bit[4],saving16Bit[5],saving16Bit[6],saving16Bit[7],saving16Bit[8],saving16Bit[9] = '0','0','0','1','1','0','0'


                result16Bit = ''.join(saving16Bit)
                binarycode.append(result16Bit)



        return binarycode



root = Tk()

#size of the window
root.geometry("400x300")

app = Application(root)
root.mainloop()
