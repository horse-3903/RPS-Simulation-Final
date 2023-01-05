from tkinter import *
from tkinter import ttk
from tkinter.messagebox import *
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from collections import Counter
import csv
import random
import re
from datetime import datetime
from os.path import exists

class RPSSingle:
    def __init__(self,root:Toplevel) -> None:
        self.root = root
        self.root.title("RPS Single Final")
        self.notebook = ttk.Notebook(root)
        self.notebook.pack()

        self.optframe = ttk.Frame(self.root,padding=5)
        self.optframe.pack()

        self.resultframe = ttk.Frame(self.root,padding=5)
        self.resultframe.pack()

        self.notebook.add(self.optframe,text="Options and Parameters")
        self.notebook.add(self.resultframe,text="Results")

        self.wr = pd.DataFrame(columns=["matchno","computer","player"])
        self.matchno = 0

        self.computer = Computer()

        self.matchlabel = Label(self.optframe,text=f"Match Number : {self.matchno}")
        self.matchlabel.grid(row=0,column=0,columnspan=3,padx=5,pady=5)

        self.rpsvallabel = Label(self.optframe,text="RPS :")
        self.rpsvallabel.grid(row=0,column=3,padx=5,pady=5)

        updown = self.root.register(self.spindir)
        self.rpsval = Spinbox(self.optframe,from_=3,to=5,increment=1,command=(updown,"%d"),width=10,relief=GROOVE)
        self.rpsval.grid(row=0,column=4,columnspan=2,padx=5,pady=5)

        self.playwr = Label(self.optframe,text="Player Win Rate : 0.0%")
        self.playwr.grid(row=1,column=0,columnspan=3,padx=5,pady=5)
        self.compwr = Label(self.optframe,text="Computer Win Rate : 0.0%")
        self.compwr.grid(row=1,column=3,columnspan=3,padx=5,pady=5)

        self.exportb = Button(self.optframe,text="Export Values",width=46,command=self.export,relief=GROOVE)
        self.exportb.grid(row=2,column=0,columnspan=6,padx=5,pady=5)

        self.inputframe = LabelFrame(self.optframe,labelanchor="n",text="Input Values")
        self.inputframe.grid(row=3,column=0,columnspan=6,padx=5,pady=5)

        self.vallabel = Label(self.inputframe,text="Input :")
        self.vallabel.grid(row=0,column=0,padx=5,pady=0)

        self.valueinput = Text(self.inputframe,width=28,height=2,relief=GROOVE,font="helvetica 10")
        self.valueinput.grid(row=1,column=0,rowspan=2,padx=5,pady=4)

        self.runsimbutton = Button(self.inputframe,width=10,text="Start",command=self.runsim,relief=GROOVE)
        self.runsimbutton.grid(row=0,column=3,padx=5,pady=2)

        self.resetsimbutton = Button(self.inputframe,width=10,text="Reset",command=self.resetsim,relief=GROOVE)
        self.resetsimbutton.grid(row=1,column=3,padx=5,pady=2)

        self.buttonframe = LabelFrame(self.optframe,labelanchor="n",text="Option Buttons")
        self.buttonframe.grid(row=4,column=0,columnspan=6,padx=5,pady=5)

        self.rbutton = Button(self.buttonframe,text="Rock",command=lambda:self.choice(0),width=12,relief=GROOVE)
        self.rbutton.grid(row=0,column=0,columnspan=2,padx=8,pady=5)

        self.pbutton = Button(self.buttonframe,text="Paper",command=lambda:self.choice(1),width=12,relief=GROOVE)
        self.pbutton.grid(row=0,column=2,columnspan=2,padx=8,pady=5)
        
        self.sbutton = Button(self.buttonframe,text="Scissors",command=lambda:self.choice(2),width=12,relief=GROOVE)
        self.sbutton.grid(row=0,column=4,columnspan=2,padx=8,pady=5)

        self.pebutton = Button(self.buttonframe,text="Pen",command=lambda:self.choice(3),width=12,relief=GROOVE)

        self.gbutton = Button(self.buttonframe,text="Glue",command=lambda:self.choice(4),width=12,relief=GROOVE)        

        # match record table
        self.matchrecord = ttk.Treeview(self.resultframe,height=30,padding=5)
        self.matchrecord.pack()

        # table columns
        self.matchrecord["columns"] = ("Index","Computer","Player","Won")
        self.matchrecord["displaycolumns"] = "#all"

        self.matchrecord.column("#0",width=0,stretch=NO)
        self.matchrecord.heading("#0",text="",anchor=CENTER)

        for col in self.matchrecord["columns"]:
            self.matchrecord.column(col,anchor=CENTER, stretch=NO, width=80)
            self.matchrecord.heading(col,anchor=CENTER,text=col)

    def resetsim(self):
        self.valueinput.delete(0.0,END)

    def runsim(self):
        instructions = self.valueinput.get(0.0,END).strip().split(" ")
        instructions = [int(i) for i in filter(lambda n: n != '\n',instructions)]
        if all(i < self.computer.rps and i >= 0 for i in instructions):
            for j in instructions:
                self.buttonframe.winfo_children()[j].invoke()
        else:
            showerror("Input Error","Value exceeds RPS Value")

    def spindir(self,direction):
        self.update_rps(direction)

    def choice(self,opt:int):
        if self.matchno > 0: 
            compopt = self.computer.option()
        else:
            compopt = random.choice(list(range(self.computer.rps)))

        self.matchno += 1
        self.matchlabel.config(text=f"Match Number : {self.matchno}")
        
        val = self.compare(compopt,opt)

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

    def compare(self,compopt,opt):
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if compopt == opt:
            self.computer.df.loc[len(self.computer.df)] = [now,self.matchno,compopt,opt,-1]
            return [compopt,opt,-1]

        if self.computer.rps == 3 or self.computer.rps == 5:
            if (compopt == 0 and opt == 3) or (compopt == 3 and opt == 4) or (compopt == 4 and opt == 2) or (compopt == 2 and opt == 1) or (compopt == 1 and opt == 0) or (compopt == 0 and opt == 2) or (compopt == 1 and opt == 4) or (compopt == 2 and opt == 3) or (compopt == 3 and opt == 1) or (compopt == 4 and opt == 0):
                self.computer.df.loc[len(self.computer.df)] = [now,self.matchno,compopt,opt,0]
                return [compopt,opt,0]
            
            elif (opt == 0 and compopt == 3) or (opt == 3 and compopt == 4) or (opt == 4 and compopt == 2) or (opt == 2 and compopt == 1) or (opt == 1 and compopt == 0) or (opt == 0 and compopt == 2) or (opt == 1 and compopt == 4) or (opt == 2 and compopt == 3) or (opt == 3 and compopt == 1) or (opt == 4 and compopt == 0):
                self.computer.df.loc[len(self.computer.df)] = [now,self.matchno,compopt,opt,1]
                return [compopt,opt,1]
            
        elif self.computer.rps == 4:
            if (compopt == 0 and opt == 2) or (compopt == 0 and opt == 3) or (compopt == 1 and opt == 0) or (compopt == 2 and opt == 1) or (compopt == 3 and opt == 1) or (compopt == 3 and opt == 2):
                self.computer.df.loc[len(self.computer.df)] = [now,self.matchno,compopt,opt,0]
                return [compopt,opt,0]
            elif (opt == 0 and compopt == 2) or (opt == 0 and compopt == 3) or (opt == 1 and compopt == 0) or (opt == 2 and compopt == 1) or (opt == 3 and compopt == 1) or (opt == 3 and compopt == 2):
                self.computer.df.loc[len(self.computer.df)] = [now,self.matchno,compopt,opt,1]
                return [compopt,opt,1]
            
    def update_rps (self,direction):
        val = askyesno("Warning","Are you sure you want to continue?\nAll of your data will be cleared")
        if val:
            self.computer.rps = int(self.rpsval.get())
            self.resetsim()

            if self.computer.rps == 3:
                self.pebutton.grid_forget()
                self.gbutton.grid_forget()
                self.matchrecord.config(height=11)

            elif self.computer.rps == 4:
                self.pebutton.grid(row=1,column=0,columnspan=6,padx=8,pady=5)
                self.gbutton.grid_forget()
                self.matchrecord.config(height=12)

            elif self.computer.rps == 5:
                self.pebutton.grid(row=1,column=0,columnspan=3,padx=8,pady=5)
                self.gbutton.grid(row=1,column=3,columnspan=3,padx=8,pady=5)
                self.matchrecord.config(height=12)

            self.matchrecord.delete(*self.matchrecord.get_children())
            self.matchno = 0
            self.computer.df = pd.DataFrame(columns=self.computer.df.columns)
            self.wr = pd.DataFrame(columns=self.wr.columns)
        else:
            cval = int(self.rpsval.get())
            self.rpsval.delete(0,END)
            if direction == 'up':
                self.rpsval.insert(0,str(cval-1))
            elif direction == 'down':
                self.rpsval.insert(0,str(cval+1))  

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

    def model1 (self):
        # predicting that it will be the winning option of the last fight
        data = self.df.tail().drop(columns=["datetime"]).stack().tolist()
        if data[-1] >= 0:
            return data[data[-1]]
        else:
            return -1

    def model2 (self):
        # predicting that it will be the least frequent in the last 5 fights
        data = self.df["player"].tail().drop(columns=["datetime"]).tolist()
        datacount = Counter(data).most_common()
        if len(datacount) > 1:
            return datacount[-1][0]
        else:
            return random.choice(list(set([0,1,2])-set(datacount[0])))

    def model3 (self):
        # predicting that it will be the most frequent in the last 5 
        data = self.df["player"].drop(columns=["datetime"]).tail().tolist()
        datacount = Counter(data).most_common()
        return datacount[0][0]
        
    def model4 (self):
        # scikit-learn decision tree classifier
        if len(self.df["player"]) >= 4:
            data = self.df["player"].tolist()
            x_train = np.array([np.array(data[i-3:i]) for i in range(3,len(data))])
            y_train = np.array([np.array(data[i]) for i in range(3,len(data))]).reshape(-1,1)
            x_predict = np.array([np.array(data[-3:])])
            model = DecisionTreeClassifier().fit(x_train,y_train)

            return model.predict(x_predict)[0]
        else:
            return -1

    def model5(self):
        # scikit-learn neural network classifier
        if len(self.df["player"]) >= 4:
            data = self.df["player"].tolist()
            x_train = np.array([np.array(data[i-3:i]) for i in range(3,len(data))])
            y_train = np.array([np.array(data[i]) for i in range(3,len(data))])
            x_predict = np.array([np.array(data[-3:])])
            model = MLPClassifier(hidden_layer_sizes=(100,100,100), max_iter=300,activation='relu',solver='adam',random_state=1).fit(x_train,y_train)

            return model.predict(x_predict)[0]
        else:
            return -1

    def model6 (self):
        # scikit-learn random forest classifier
        if len(self.df["player"]) >= 4:
            data = self.df["player"].tolist()
            x_train = np.array([np.array(data[i-3:i]) for i in range(3,len(data))])
            y_train = np.array([np.array(data[i]) for i in range(3,len(data))])
            x_predict = np.array([np.array(data[-3:])])
            model = RandomForestClassifier(n_estimators=20).fit(x_train,y_train)

            return model.predict(x_predict)[0]
        else:
            return -1

    def beats (self,opt:int):
        if self.rps == 3:
            if opt == 0:
                return 1
            elif opt == 1:
                return 2
            elif opt == 2:
                return 0
            else:
                return -1

        elif self.rps == 4:
            if opt == 0:
                return 1
            elif opt == 1:
                return random.choice([2,3])
            elif opt == 2:
                return random.choice([0,3])
            elif opt == 3:
                return 0

        elif self.rps == 5:
            if opt == 0:
                return random.choice([1,4])
            elif opt == 1:
                return random.choice([2,3])
            elif opt == 2:
                return random.choice([0,4])
            elif opt == 3:
                return random.choice([0,2])
            elif opt == 4:
                return random.choice([1,3])
            else:
                return -1

    def option (self):
        optlist = [j for j in [self.beats(i) for i in [self.model1(),self.model2(),self.model3(),self.model4(),self.model5(),self.model6()]] if (j != -1) and (j != None)]
        val,freq = np.split(np.array(Counter(optlist).most_common()),2,axis=1)
        val = val.flatten().tolist()
        freq = freq.flatten().tolist()
        return val[0] 
                