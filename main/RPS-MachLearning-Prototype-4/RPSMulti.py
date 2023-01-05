from tkinter.messagebox import *
from tkinter import ttk
from tkinter import *
import random
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from collections import Counter,OrderedDict
import csv
import random
from os.path import exists

class RPSMulti:
    
    def __init__(self,root:Toplevel or Tk):
        self.root = root
        self.root.title("RPS Multi Final")
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack()

        self.simrunning = False
        self.exit = False
        self.root.protocol("WM_DELETE_WINDOW", self.closing)
        
        self.optframe = ttk.Frame(self.root,padding=5)
        self.optframe.pack(fill=BOTH)

        self.resultframe = ttk.Frame(self.root,padding=5)
        self.resultframe.pack(fill=BOTH)

        self.notebook.add(self.optframe,text="Options and Parameters")
        self.notebook.add(self.resultframe,text="Results")

        self.df = pd.DataFrame(columns=["matchno","P0","C0","won"])
        self.matchstart = False
        self.matchno = 0

        # self.optframe
        self.playervallabel = Label(self.optframe,text="Players :")
        self.playervallabel.grid(row=0,column=0,columnspan=2,padx=2,pady=2)

        playerupdown = self.root.register(self.updateplayer)
        self.playerval = Spinbox(self.optframe,from_=1,to=2,width=8,relief=GROOVE,command=(playerupdown,"%d"))
        self.playerval.grid(row=1,column=0,columnspan=2,padx=2,pady=2)

        self.playlst = [Player(self,self.optframe,0)]

        self.compvallabel = Label(self.optframe,text="Computers :")
        self.compvallabel.grid(row=0,column=2,columnspan=2,padx=2,pady=2)

        compupdown = self.root.register(self.updatecomp)
        self.compval = Spinbox(self.optframe,from_=1,to=2,width=8,relief=GROOVE,command=(compupdown,"%d"))
        self.compval.grid(row=1,column=2,columnspan=2,padx=2,pady=2)

        self.complst = [Computer(self,self.optframe,0)]

        self.choicedict = {
            "P0":-1,
            "C0":-1
        }

        self.startstop = Button(self.optframe,text="Start Match",width=10,command=self.startstopmatch,relief=GROOVE)
        self.startstop.grid(row=0,column=4,columnspan=2,padx=5,pady=5)

        self.exportbutton = Button(self.optframe,text="Export",width=10,command=self.export,relief=GROOVE)
        self.exportbutton.grid(row=1,column=4,columnspan=2,padx=5,pady=5)

        self.vallabel = Label(self.optframe,text="Input :")
        self.vallabel.grid(row=2,rowspan=2,column=0,padx=5,pady=5)

        self.valinput = Text(self.optframe,height=2,width=20,relief=GROOVE,font="helvetica 10")
        self.valinput.grid(row=2,rowspan=2,column=1,columnspan=3,sticky=W)
        self.valinput.insert(0.0,"P0 : ")

        self.valcurrent = "P0 : "

        self.startsimb = Button(self.optframe,text="Start Sim",width=10,command=self.startsim,relief=GROOVE)
        self.startsimb.grid(row=2,column=4,columnspan=2,padx=5,pady=5)

        self.contsimb = Button(self.optframe,text="Repeat",width=10,command=self.contsim,relief=GROOVE)
        self.contsimb.grid(row=3,column=4,columnspan=2,padx=5,pady=5)

        self.compareframe = LabelFrame(self.optframe,labelanchor='n',text="Compare")
        self.compareframe.grid(row=0,rowspan=5,column=6,columnspan=2,padx=5,pady=5,sticky=NE)

        self.play0label = Label(self.compareframe,text="P0 : None")
        self.play0label.grid(row=0,column=0,padx=5,pady=5,sticky=W)

        self.comp0label = Label(self.compareframe,text="C0 : None")
        self.comp0label.grid(row=1,column=0,padx=5,pady=5,sticky=W)

        self.play1label = Label(self.compareframe,text="P1 : None")
        self.play1label.grid(row=0,column=1,padx=5,pady=5,sticky=W)

        self.comp1label = Label(self.compareframe,text="C1 : None")
        self.comp1label.grid(row=1,column=1,padx=5,pady=5,sticky=W)

        self.won = Label(self.compareframe,text="Won : None")
        self.won.grid(row=2,column=0,padx=5,pady=5)

        self.continued = BooleanVar()
        self.contbutton = Button(self.compareframe,text="Continue",width=8,relief=GROOVE,command=lambda: self.continued.set(not self.continued.get()))
        self.contbutton.grid(row=2,column=1,padx=5,pady=5)

        # self.resultframe
        self.matchrecord = ttk.Treeview(self.resultframe,height=9)
        self.matchrecord.pack(side=LEFT,padx=5,pady=5)
        self.matchrecord.bind("<Control-c>",self.copyvalues)

        self.recscroll = Scrollbar(self.resultframe,orient=VERTICAL,relief=FLAT)
        self.recscroll.pack(side=RIGHT,fill=Y)

        self.matchrecord.config(yscrollcommand=self.recscroll.set)
        self.recscroll.config(command=self.matchrecord.yview)

        # table columns
        self.matchrecord["columns"] = ("Match No.","Player 0","Comp 0","Player 1","Comp 1","Won")
        
        tempcols = ()
        for i in range(len(self.df.columns.to_list()[1:-1])):
            dfval = self.df.columns.to_list()[1:-1][i]
            for j in self.matchrecord["columns"]:
                if dfval[0] in j and dfval[1] in j:
                    tempcols += (j,)

        self.matchrecord["displaycolumns"] = ("Match No.",) + tempcols + ("Won",)

        self.matchrecord.column("#0",width=0,stretch=NO)
        self.matchrecord.heading("#0",text="",anchor=CENTER)
        self.cellwidth = 117

        for col in self.matchrecord["columns"]:
            self.matchrecord.column(col,anchor=CENTER, stretch=NO, width=self.cellwidth)
            self.matchrecord.heading(col,anchor=CENTER,text=col)

    def contsim(self):
        if self.matchstart:
            try:
                vals = {int(name[1]) : [int(i) for i in ins.split(" ")] for name,ins in [i.strip().split(" : ") for i in self.valinput.get(0.0,END).strip().split("\n")]}
                length = len(set([len(l) for l in vals.values()]) if len([len(l) for l in vals.values()]) > 1 else [len(l) for l in vals.values()])

                if max(sum(vals.values(),[])) <= 2 and length == 1:
                    self.simrunning = True
                    
                    if len(vals.keys()) == 1:
                        player = self.playlst[0]
                        idx = 0
                        while idx < len(list(vals.values())[0]):
                            player.buttonframe.winfo_children()[:3][list(vals.values())[0][idx]].invoke()
                            idx += 1

                    elif len(vals.keys()) == 2:
                        player1,player2 = self.playlst
                        idx = 0
                        
                        while idx < len(list(vals.values())[0]):
                            player1.buttonframe.winfo_children()[:3][list(vals.values())[0][idx]].invoke()
                            player2.buttonframe.winfo_children()[:3][list(vals.values())[1][idx]].invoke()
                            idx += 1
                    
                    self.simrunning = False
            except:
                showerror("Error","Something went wrong,\nPlease try again")
                self.valinput.delete(0.0,END)
                self.valinput.insert(0.0,self.valcurrent)


    def startsim(self):
        if not self.matchstart:
            try:
                vals = {int(name[1]) : [int(i) for i in ins.split(" ")] for name,ins in [i.strip().split(" : ") for i in self.valinput.get(0.0,END).strip().split("\n")]}
                length = len(set([len(l) for l in vals.values()]) if len([len(l) for l in vals.values()]) > 1 else [len(l) for l in vals.values()])

                if max(sum(vals.values(),[])) <= 2 and length == 1:
                    self.simrunning = True
                    self.startstopmatch()
                    
                    if len(vals.keys()) == 1:
                        player = self.playlst[0]
                        idx = 0
                        while idx < len(list(vals.values())[0]):
                            player.buttonframe.winfo_children()[:3][list(vals.values())[0][idx]].invoke()
                            idx += 1

                    elif len(vals.keys()) == 2:
                        player1,player2 = self.playlst
                        idx = 0
                        
                        while idx < len(list(vals.values())[0]):
                            player1.buttonframe.winfo_children()[:3][list(vals.values())[0][idx]].invoke()
                            player2.buttonframe.winfo_children()[:3][list(vals.values())[1][idx]].invoke()
                            idx += 1
                    
                    self.simrunning = False
            except:
                showerror("Error","Something went wrong,\nPlease try again")
                self.valinput.delete(0.0,END)
                self.valinput.insert(0.0,self.valcurrent)

    def sortdict(self,cols):
        tempdict = OrderedDict()
        for i in range(len(cols)):
            tempdict[cols[i]] = self.choicedict[cols[i]]
        self.choicedict = dict(tempdict)

    def export(self):
        data = self.df.rename(columns={"matchno":"Match Number"} | {i:i.capitalize()[0]+i[-1] for i in self.df.columns.to_list()[1:-1]} | {"won":"Won"})
        if exists("./rps-results.csv"):
            addlst = data.values.tolist()
        else:
            addlst = [data.columns.tolist()]+data.values.tolist()

        with open('rps-results.csv','a',newline='') as file:
                writer = csv.writer(file)
                writer.writerows(addlst)
        file.close()

    def closing(self):
        self.root.destroy()
        self.root.update()

    def resetopt (self):
        for comp in self.complst:
            self.choicedict[f"C{comp.index}"] = -1
            comp.chosenval.config(text="No",fg="red")
            comp.winrate.config(text="Win Rate : 0.00%")
        for player in self.playlst:
            self.choicedict[f"P{player.index}"] = -1
            player.chosenval.config(text="No",fg="red")
            player.winrate.config(text="Win Rate : 0.00%")
        for widget in self.compareframe.winfo_children()[:-1]:
            widget.config(text=widget.cget("text")[:widget.cget("text").find(": ")]+": None")

    def updateheight (self):
        self.root.update()
        self.matchrecord.update()
        rowno = int((self.root.winfo_height()-26)/20) - 2
        self.matchrecord.config(height=rowno)

    def updatecols (self):
        self.root.update()
        tempcols = ()
        for i in range(len(self.df.columns.to_list()[1:-1])):
            dfval = self.df.columns.to_list()[1:-1][i]
            for j in self.matchrecord["columns"]:
                if dfval[0] in j and dfval[1] in j:
                    tempcols += (j,)

        self.matchrecord["displaycolumns"] = ("Match No.",) + tempcols + ("Won",)
        self.cellwidth = round(468/len(self.matchrecord["displaycolumns"]))

        for col in self.matchrecord["columns"]:
            self.matchrecord.column(col,anchor=CENTER, stretch=NO, width=self.cellwidth)
            self.matchrecord.heading(col,anchor=CENTER,text=col)

    def copyvalues(self,event):
        values = "\t".join(self.matchrecord["columns"]) + "\n"
        for id in self.matchrecord.selection():
            values += "\t".join(list(self.matchrecord.item(id,"values"))) + "\n"
        self.root.clipboard_clear()
        self.root.clipboard_append(values)

    def startstopmatch (self):
        if "Start" in self.startstop.cget('text'):
            self.matchstart = True
            for comp in self.complst:
                comp.choose()
            self.startstop.config(text="Stop Match")
            
        elif "Stop" in self.startstop.cget('text') and askyesno("Warning","Are you sure you want to continue?"):
            self.matchstart = False
            self.resetopt()
            self.startstop.config(text="Start Match")
            self.resetdata()

        self.matchno = 0

    def checkall (self):
        values = list(self.choicedict.values())
        if -1 not in values: 
            self.compare()

    def compare (self):
        values = list(self.choicedict.values())
        compwidgetlst = [j for j in self.compareframe.winfo_children()[:-1] if j.cget("text")[:2] in [i.capitalize()[0]+i[-1] for i in self.df.columns[:-1]]]
        for i in range(len(values)):
            widget = compwidgetlst[i]
            opt = ["Rock","Paper","Scissors"][values[i]]
            widget.config(text=widget.cget("text")[:widget.cget("text").find(": ")]+f": {opt}")

        insval = [self.choicedict[i] if i in self.choicedict.keys() else '-' for i in [j[0]+j[-1] for j in list(self.matchrecord["columns"])][1:-1]]

        if len(set(values)) <= 2:
            if len(set(values)) == 1:
                # Tie - Same Val
                self.won.config(text="Won : Tie")
                self.df.loc[len(self.df)] = [len(self.df)]+values+["Tie"]
                record = [len(self.matchrecord.get_children())] + [["Rock","Paper","Scissors"][i] if type(i) == int else i for i in insval] + ["Tie"]
            else:
                opt1,opt2 = list(set(values))
                if (opt1 == 0 and opt2 == 2) or (opt1 == 1 and opt2 == 0) or (opt1 == 2 and opt2 == 1):
                    option = [opt1,opt2]
                elif (opt2 == 0 and opt1 == 2) or (opt2 == 1 and opt1 == 0) or (opt2 == 2 and opt1 == 1):
                    option = [opt2,opt1]

                vals = [True if i == option[0] else False for i in values]
                record = [len(self.matchrecord.get_children())] + [["Rock","Paper","Scissors"][i] if type(i) == int else i for i in insval] + [",".join([list(self.choicedict.keys())[j] for j in [i for i,val in enumerate(vals) if val == True]])]
                self.df.loc[len(self.df)] = [len(self.df)]+values+[record[-1]]
                self.won.config(text=f"Won : {record[-1]}")
                
        else:
            record = [len(self.matchrecord.get_children())] + [["Rock","Paper","Scissors"][i] if type(i) == int else i for i in insval] + ["Tie"]
            self.won.config(text="Won : None")
            self.df.loc[len(self.df)] = [len(self.df)]+values+["None"]
        
        winlst = np.array([i.split(",") for i in self.df["won"].to_list() if i != "None" and i != "Tie"])
        if len(winlst) > 0:
            winlst = np.hstack(winlst).tolist()
            for val,no in Counter(winlst).most_common():
                if val[0] == "P":
                    self.playlst[int(val[1])].winrate.config(text=f"Win Rate : {round((no/len(winlst))*100,2)}%")
                else:
                    self.complst[int(val[1])].winrate.config(text=f"Win Rate : {round((no/len(winlst))*100,2)}%")

        self.matchrecord.insert(parent="",index=END,iid=len(self.matchrecord.get_children()),text="",values=record)

        if self.simrunning:
            for comp in self.complst:
                self.choicedict[f"C{comp.index}"] = -1
                comp.chosenval.config(text="No",fg="red")
            for player in self.playlst:
                self.choicedict[f"P{player.index}"] = -1
                player.chosenval.config(text="No",fg="red")
            self.matchno += 1
        else:
            self.contbutton.wait_variable(self.continued)
            if not self.exit:
                for comp in self.complst:
                    self.choicedict[f"C{comp.index}"] = -1
                    comp.chosenval.config(text="No",fg="red")
                for player in self.playlst:
                    self.choicedict[f"P{player.index}"] = -1
                    player.chosenval.config(text="No",fg="red")
                self.matchno += 1

        for comp in self.complst:
            comp.choose()

    def resetdata(self):
        self.matchrecord.delete(*self.matchrecord.get_children())
        self.df = pd.DataFrame(columns=self.df.columns)

    def updatecomp (self,direction):
        val = int(self.compval.get())
        if (len(self.complst) == 1 and direction == 'down') or (len(self.complst) == 2 and direction == 'up'):
            pass
        else:
            if askyesno("Warning","Are you sure you want to continue?"):
                self.matchno = 0
                if direction == 'up':
                    self.complst.append(Computer(self,self.optframe,val-1))                    
                elif direction == 'down':
                    self.complst[-1].buttonframe.grid_forget()
                    del self.complst[-1]

                cols = self.df.columns.tolist()
                zero,ones = [i for i in cols if '0' in i],[i for i in cols if '1' in i]
                if direction == 'up':
                    ones.append(f'C{val-1}')
                    self.choicedict[f"C{val-1}"] = -1
                else:
                    ones = ones[:-1]
                    del self.choicedict[f"C{val}"]

                self.df = pd.DataFrame(columns=dict.fromkeys(["matchno"]+zero+ones+["won"]))
                self.sortdict(zero+ones)
                self.updateheight()
                self.updatecols()
                self.resetopt()
                self.resetdata()
                for comp in self.complst:
                    comp.winrate.config(text="Win Rate : 0.00%")
                for player in self.playlst:
                    player.winrate.config(text="Win Rate : 0.00%") 
            else:
                self.compval.delete(0,END)
                if direction == 'up':
                    self.compval.insert(0,str(val-1))
                elif direction == 'down':
                    self.compval.insert(0,str(val+1))

    def updateplayer (self,direction):
        val = int(self.playerval.get())
        if (len(self.playlst) == 1 and direction == 'down' or (len(self.playlst) == 2 and direction == 'up')):
            pass
        else:
            if askyesno("Warning","Are you sure you want to continue?"):
                self.matchno = 0
                if direction == 'up':
                    self.playlst.append(Player(self,self.optframe,val-1))
                    self.valinput.insert(END,f"\nP{val-1} : ")
                elif direction == 'down':
                    self.playlst[-1].buttonframe.grid_forget()
                    del self.playlst[-1]
                    self.valinput.delete(float(val+1),END)
                
                self.valcurrent = "\n".join([i[:i.find(": ")]+": " for i in self.valinput.get(0.0,END).split("\n")])

                cols = self.df.columns.to_list()
                zero,ones = [i for i in cols if '0' in i],[i for i in cols if '1' in i]
                if direction == 'up':
                    ones.insert(0,f'P{val-1}')
                    self.choicedict[f"P{val-1}"] = -1
                else:
                    ones = ones[:-1]
                    del self.choicedict[f"P{val}"]

                self.df = pd.DataFrame(columns=dict.fromkeys(["matchno"]+zero+ones+["won"]))
                self.sortdict(zero+ones)
                self.updateheight()
                self.updatecols()
                self.resetopt()
                self.resetdata()

                for comp in self.complst:
                    comp.winrate.config(text="Win Rate : 0.00%")
                for player in self.playlst:
                    player.winrate.config(text="Win Rate : 0.00%") 
            else:
                self.playerval.delete(0,END)
                if direction == 'up':
                    self.playerval.insert(0,str(val-1))
                elif direction == 'down':
                    self.playerval.insert(0,str(val+1))

class Computer:
    def __init__(self,platform:RPSMulti,master:Frame,index:int):
        self.platform = platform
        self.index = index
        self.frame = master
        self.buttonframe = LabelFrame(self.frame,labelanchor="n",text=f"Computer {self.index}")
        
        self.buttonframe.grid(row=self.index+5,column=7,columnspan=3,padx=10,pady=7)

        self.winrate = Label(self.buttonframe,text="Win Rate : 0.00%",width=15)
        self.winrate.grid(row=0,column=0,columnspan=2,padx=8,pady=5)

        self.chosen = Label(self.buttonframe,text="Chosen :",width=9)
        self.chosen.grid(row=1,column=0,pady=5)

        self.chosenval = Label(self.buttonframe,text="No",fg="red",font="roboto 12 bold",width=6)
        self.chosenval.grid(row=1,column=1,pady=5)

    def model1 (self):
        # predicting that it will be the winning option of the last fight
        index = self.platform.df.iloc[-1]["won"].split(",")[0] if self.platform.df.iloc[-1]["won"] != "Tie" and self.platform.df.iloc[-1]["won"] != "None" else "P0"
        if len(self.platform.playlst) == 1:
            return self.platform.df.iloc[-1][index]
        else:
            return [self.platform.df.iloc[-1][index],self.platform.df.iloc[-1][index]]

    def model2 (self):
        # predicting that it will be the least frequent
        results = []
        for i in [j for j in list(self.platform.df.columns) if "P" in j]:
            counts = Counter(self.platform.df[i].tolist()).most_common()
            results.append(random.choice([val1 for val1,no1 in counts if no1 == max([no2 for val2,no2 in counts])]))
        if len(results) < 1:
            return -1
        else:
            return np.hstack(np.array(results)).tolist()

    def model3 (self):
        # predicting that it will be the most frequent
        results = []
        for i in [j for j in list(self.platform.df.columns) if "P" in j]:
            counts = Counter(self.platform.df[i].tolist()).most_common()
            results.append(random.choice([val1 for val1,no1 in counts if no1 == min([no2 for val2,no2 in counts])]))
        if len(results) < 1:
            return -1
        else:
            return np.hstack(np.array(results)).tolist()
        
    def model4 (self):
        # scikit-learn decision tree classifier
        if len(self.platform.df["P0"]) >= 4:
            results = []
            for col in [i for i in self.platform.df.columns.to_list()[1:-1] if "C" not in i ]:
                data = self.platform.df[col].tolist()
                x_train = np.array([np.array(data[i-3:i]) for i in range(3,len(data))])
                y_train = np.array([np.array(data[i]) for i in range(3,len(data))]).reshape(-1,1)
                x_predict = np.array([np.array(data[-3:])])
                model = DecisionTreeClassifier().fit(x_train,y_train)
                results.append(model.predict(x_predict)[0])

            return results
        else:
            return -1

    def model5(self):
        # scikit-learn neural network classifier
        if len(self.platform.df["P0"]) >= 4:
            results = []
            for col in [i for i in self.platform.df.columns.to_list()[1:-1] if "C" not in i]:
                data = self.platform.df[col].tolist()
                x_train = np.array([np.array(data[i-3:i]) for i in range(3,len(data))])
                y_train = np.array([np.array(data[i]) for i in range(3,len(data))])
                x_predict = np.array([np.array(data[-3:])])
                model = MLPClassifier(hidden_layer_sizes=(100,100,100), max_iter=300,activation='relu',solver='adam',random_state=1).fit(x_train,y_train)
                results.append(model.predict(x_predict)[0])

            return results
        else:
            return -1

    def model6 (self):
        # scikit-learn random forest classifier
        if len(self.platform.df["P0"]) >= 4:
            results = []
            for col in [i for i in self.platform.df.columns.to_list()[1:-1] if "C" not in i]:
                data = self.platform.df[col].tolist()
                x_train = np.array([np.array(data[i-3:i]) for i in range(3,len(data))])
                y_train = np.array([np.array(data[i]) for i in range(3,len(data))])
                x_predict = np.array([np.array(data[-3:])])
                model = RandomForestClassifier(n_estimators=20).fit(x_train,y_train)
                results.append(model.predict(x_predict)[0])

            return results
        else:
            return -1

    def beats (self,opt:int):
        if opt == 0:
            return 1
        elif opt == 1:
            return 2
        elif opt == 2:
            return 0
        else:
            return -1

    def choose(self):
        if self.platform.matchstart and not self.platform.exit:
            if self.platform.matchno == 0:
                opt = random.choice(list(range(3)))
            else:
                if len(self.platform.playlst) == 1:
                    data = np.hstack(np.array([i for i in [self.model1(),self.model2(),self.model3(),self.model4(),self.model5(),self.model6()] if i != -1])).tolist()
                    optlist = [j for j in [self.beats(i) for i in data]]
                elif len(self.platform.playlst) == 2:
                    data = [i for i in [self.model1(),self.model2(),self.model3(),self.model4(),self.model5(),self.model6()] if i != -1]
                    play0,play1 = [i for i,j in data],[j for i,j in data]
                    p0win,p1win = 0,0

                    for i in range(len(play0)):
                        v0,v1 = play0[i],play1[i]
                        if self.beats(v0) == v1:
                            p1win += 1
                        elif self.beats(v1) == v0:
                            p0win += 1
                    
                    if p0win > p1win:
                        optlist = [j for j in [self.beats(i) for i in play1]]
                    elif p0win < p1win:
                        optlist = [j for j in [self.beats(i) for i in play0]]
                    else:
                        optlist = random.choice([[j for j in [self.beats(i) for i in play0]],[j for j in [self.beats(i) for i in play1]]])

                counts = Counter(optlist).most_common()
                opt = random.choice([val1 for val1,no1 in counts if no1 == max([no2 for val2,no2 in counts])])
            
            self.chosenval.config(text="Yes",fg="green")
            self.platform.choicedict[f"C{self.index}"] = opt

class Player:
    def __init__(self,platform:RPSMulti,master:Frame,index:int):
        self.platform = platform
        self.index = index
        self.frame = master
        self.buttonframe = LabelFrame(self.frame,labelanchor="n",text=f"Player {self.index}")
        self.buttonframe.grid(row=self.index+5,column=0,columnspan=6,padx=10,pady=7)

        self.rbutton = Button(self.buttonframe,text="Rock",command=lambda:self.choose(0),width=11,relief=GROOVE)
        self.rbutton.grid(row=0,column=0,columnspan=2,padx=8,pady=5)

        self.pbutton = Button(self.buttonframe,text="Paper",command=lambda:self.choose(1),width=11,relief=GROOVE)
        self.pbutton.grid(row=0,column=2,columnspan=2,padx=8,pady=5)
        
        self.sbutton = Button(self.buttonframe,text="Scissors",command=lambda:self.choose(2),width=11,relief=GROOVE)
        self.sbutton.grid(row=0,column=4,columnspan=2,padx=8,pady=5)

        self.winrate = Label(self.buttonframe,text="Win Rate : 0.00%")
        self.winrate.grid(row=1,column=0,columnspan=4,padx=5,pady=5)

        self.chosen = Label(self.buttonframe,text="Chosen :")
        self.chosen.grid(row=1,column=3,columnspan=2,padx=7,pady=5)

        self.chosenval = Label(self.buttonframe,text="No",fg="red",font="roboto 12 bold")
        self.chosenval.grid(row=1,column=4,columnspan=2,padx=5,pady=5)

    def choose(self,opt):
        if self.platform.matchstart:
            if self.chosenval.cget("text") == "No":
                self.platform.choicedict[f"P{self.index}"] = opt
                self.chosenval.config(text="Yes",fg="green")
                self.platform.checkall()
            elif self.chosenval.cget("text") == "Yes":
                self.platform.choicedict[f"P{self.index}"] = -1
                self.chosenval.config(text="No",fg="red")

root = Tk()
RPSMulti(root)
root.mainloop()