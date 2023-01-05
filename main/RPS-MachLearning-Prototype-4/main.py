from tkinter import *
from tkinter import ttk
from tkinter.messagebox import *
from RPSMulti import RPSMulti
from RPSSingle import RPSSingle
from random import randrange

def generate():
    root.clipboard_clear()
    root.clipboard_append(' '.join([str(randrange(0,int(rpsval.get()))) for i in range(int(lenval.get()))]))

root = Tk()
root.title("RPS Simulation Master Window Final")
nb = ttk.Notebook(root)
nb.pack()

bframe = ttk.Frame(root,padding=10)
bframe.pack()

gframe = ttk.Frame(root,padding=10)
gframe.pack()

nb.add(bframe,text="Open Simulator")
nb.add(gframe,text="Generate Input")

single = Button(bframe,text="RPS (Single Player)",width=24,command=lambda: RPSSingle(Toplevel(root)),relief=GROOVE)
multi = Button(bframe,text="RPS (Multiple Players)",width=24,command=lambda: RPSMulti(Toplevel(root)),relief=GROOVE)

single.pack(side=TOP,padx=5,pady=2)
multi.pack(side=BOTTOM,padx=5,pady=2)

rpslabel = Label(gframe,text="RPS :",width=7)
rpslabel.grid(row=0,column=0,pady=5,sticky=W)

rpsval = Spinbox(gframe,from_=3,to=5,width=7)
rpsval.grid(row=0,column=1,padx=5,pady=5,sticky=W)

lenlabel = Label(gframe,text="Length :",width=7)
lenlabel.grid(row=0,column=2,pady=5,sticky=W)

lenval = Spinbox(gframe,from_=10,to=30,increment=5,width=7)
lenval.grid(row=0,column=3,pady=5,sticky=W)

gbutton = Button(gframe,text="Generate Values (to Clipboard)",width=32,command=generate,relief=GROOVE)
gbutton.grid(row=1,column=0,columnspan=4,padx=5,pady=5)

root.mainloop()