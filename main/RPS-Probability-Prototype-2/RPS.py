from tkinter import *
from tkinter import ttk
from tkinter.messagebox import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
from datetime import datetime
from os.path import exists

class RPSTest:
    def __init__(self,root) -> None:
        self.root = root
        self.frame = Frame(self.root)
        self.frame.pack()
        self.wr = pd.DataFrame(columns=["matchno","computer","player"])
        self.matchno = 0

        self.computer = Computer()

        self.matchlabel = Label(self.frame,text=f"Match Number : {self.matchno}")
        self.matchlabel.grid(row=0,column=0,columnspan=3,padx=5,pady=5)

        self.rpsvallabel = Label(self.frame,text="RPS :")
        self.rpsvallabel.grid(row=0,column=3,padx=5,pady=5)

        self.rpsval = Spinbox(self.frame,from_=3,to=5,increment=3,command=self.update_rps,relief=GROOVE)
        self.rpsval.grid(row=0,column=4,columnspan=2,padx=5,pady=5)

        self.playwr = Label(self.frame,text="Player Win Rate : 0.0%")
        self.playwr.grid(row=1,column=0,columnspan=3,padx=5,pady=5)
        self.compwr = Label(self.frame,text="Computer Win Rate : 0.0%")
        self.compwr.grid(row=1,column=3,columnspan=3,padx=5,pady=5)

        self.plotb = Button(self.frame,text="Graph Values",width=20,command=self.plot,relief=GROOVE)
        self.plotb.grid(row=2,column=0,columnspan=3,padx=5,pady=5)

        self.exportb = Button(self.frame,text="Export Values",width=20,command=self.export,relief=GROOVE)
        self.exportb.grid(row=2,column=3,columnspan=3,padx=5,pady=5)

        self.buttonframe = LabelFrame(self.frame,labelanchor="n",text="Option Buttons")
        self.buttonframe.grid(row=3,column=0,columnspan=6,padx=5,pady=5)

        self.rbutton = Button(self.buttonframe,text="Rock",command=lambda:self.choice(0),width=12,relief=GROOVE)
        self.rbutton.grid(row=0,column=0,columnspan=2,padx=8,pady=5)

        self.pbutton = Button(self.buttonframe,text="Paper",command=lambda:self.choice(1),width=12,relief=GROOVE)
        self.pbutton.grid(row=0,column=2,columnspan=2,padx=8,pady=5)
        
        self.sbutton = Button(self.buttonframe,text="Scissors",command=lambda:self.choice(2),width=12,relief=GROOVE)
        self.sbutton.grid(row=0,column=4,columnspan=2,padx=8,pady=5)

        self.pebutton = Button(self.buttonframe,text="Pen",command=lambda:self.choice(3),width=12,relief=GROOVE)

        self.gbutton = Button(self.buttonframe,text="Glue",command=lambda:self.choice(4),width=12,relief=GROOVE)        

        # match record table
        self.matchrecord = ttk.Treeview(self.frame,height=18,padding=5)
        self.matchrecord.grid(row=4,column=0,columnspan=6,padx=5,pady=5)

        # table columns
        self.matchrecord["columns"] = ("Index","Computer","Player","Won")
        self.matchrecord["displaycolumns"] = "#all"

        self.matchrecord.column("#0",width=0,stretch=NO)
        self.matchrecord.heading("#0",text="",anchor=CENTER)

        for col in self.matchrecord["columns"]:
            self.matchrecord.column(col,anchor=CENTER, stretch=NO, width=80)
            self.matchrecord.heading(col,anchor=CENTER,text=col)

    def choice(self,opt:int):
        compopt = self.computer.option()

        self.matchno += 1
        self.matchlabel.config(text=f"Match Number : {self.matchno}")
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if compopt == opt:
            self.computer.df.loc[len(self.computer.df)] = [now,self.matchno,compopt,opt,-1]
            val = [compopt,opt,-1]

        elif (compopt == 0 and opt == 3) or (compopt == 3 and opt == 4) or (compopt == 4 and opt == 2) or (compopt == 2 and opt == 1) or (compopt == 1 and opt == 0) or (compopt == 0 and opt == 2) or (compopt == 1 and opt == 4) or (compopt == 2 and opt == 3) or (compopt == 3 and opt == 1) or (compopt == 4 and opt == 0):
            self.computer.df.loc[len(self.computer.df)] = [now,self.matchno,compopt,opt,0]
            val = [compopt,opt,0]
        
        elif (opt == 0 and compopt == 3) or (opt == 3 and compopt == 4) or (opt == 4 and compopt == 2) or (opt == 2 and compopt == 1) or (opt == 1 and compopt == 0) or (opt == 0 and compopt == 2) or (opt == 1 and compopt == 4) or (opt == 2 and compopt == 3) or (opt == 3 and compopt == 1) or (opt == 4 and compopt == 0):
            self.computer.df.loc[len(self.computer.df)] = [now,self.matchno,compopt,opt,1]
            val = [compopt,opt,1]

        val[2] = ["Computer","Player","Draw"][val[2]]
        self.matchrecord.insert(parent="",index=END,iid=len(self.matchrecord.get_children()),text="",values=(len(self.matchrecord.get_children()),)+tuple(val))        
        self.matchrecord.yview_moveto(1)
        data = self.computer.df["won"].value_counts(normalize=True).to_frame().transpose() * 100
        for i in [-1,0,1]:
            if i not in data.columns:
                data[i] = 0.0
        self.pwr = round(data[1].item(),1)
        self.cwr = round(data[0].item(),1)
        self.playwr.config(text=f"Player Win Rate : {self.pwr}%")
        self.compwr.config(text=f"Computer Win Rate : {self.cwr}%")
        self.wr.loc[len(self.wr)] = [self.matchno,self.cwr,self.pwr]

    def update_rps (self):
        val = askyesno("Warning","Are you sure you want to continue?\nAll of your data will be cleared")
        if val:
            self.computer.rps = int(self.rpsval.get())

            if self.computer.rps == 3:
                self.pebutton.grid_forget()
                self.gbutton.grid_forget()
                self.matchrecord.config(height=18)

            elif self.computer.rps == 5:
                self.pebutton.grid(row=1,column=0,columnspan=3,padx=8,pady=5)
                self.gbutton.grid(row=1,column=3,columnspan=3,padx=8,pady=5)
                self.matchrecord.config(height=16)

            self.matchrecord.delete(*self.matchrecord.get_children())
            self.matchno = 0
            self.computer.df = pd.DataFrame(columns=self.computer.df.columns)
            self.wr = pd.DataFrame(columns=self.wr.columns)
        else:
            currentval = int(self.rpsval.get())
            self.rpsval.delete(0,END)
            if currentval == 3:
                self.rpsval.insert(0,'5')
            else:
                self.rpsval.insert(0,'3')

    def plot (self):
        fig,ax1 = plt.subplots()

        x,y1,y2 = self.wr["matchno"].to_numpy(),self.wr["computer"].to_numpy(),self.wr["player"].to_numpy()
        ax1.plot(x,y1,"b-o",label="Computer")
        ax1.plot(x,y2,"r-o",label="Player")
        ax1.legend()
        ax1.set_ylabel("Win Rate (%)")
        ax1.set_title("Win Rate against Match Number")

        plt.show()
        

    def export (self):
        data = self.computer.df.rename(columns={"datetime":"Date/Time","matchno":"Match Number","comp":"Computer","player":"Player","won":"Won"})
        if exists("./rps-results.csv"):
            addlst = data.values.tolist()
        else:
            addlst = [data.columns.tolist()]+data.values.tolist()

        with open('rps-results.csv','a',newline='') as file:
                writer = csv.writer(file)
                writer.writerows(addlst)
        file.close()

        
class Computer:
    def __init__(self) -> None:
        self.df = pd.DataFrame(columns=["datetime","matchno","comp","player","won"])
        self.rps = 3

    def option (self):
        optlst = np.random.multinomial(100,[1/3]*3).tolist()
        return optlst.index(max(optlst))
                
root = Tk()
root.title("RPS Prototype 1")
root.geometry("360x570")
test = RPSTest(root)
root.mainloop()