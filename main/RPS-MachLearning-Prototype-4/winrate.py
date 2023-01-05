import csv
from tkinter import *

with open("rps-results.csv") as file:
    r = csv.reader(file,delimiter=",")
    wlst = []
    p0,p1,c0,c1 = 0,0,0,0
    idx = 1
    rval = "\t".join(["Match No.","Average Player WR","Average Comp WR"])
    for row in list(r)[1:]:
        val = row[-1].split(",")
        for p in val:
            if p == "P0":
                p0 += 1
            elif p == "P1":
                p1 += 1
            elif p == "C0":
                c0 += 1
            elif p == "C1":
                c1 += 1
        rval += "\n" + "\t".join([str(idx-1)]+[str(i)+"%" for i in [round(i*100,2) for i in [(p0/idx+p1/idx)/2,(c0/idx+c1/idx)/2]]])
        idx += 1

    print(rval)

root = Tk()
root.clipboard_clear()
root.clipboard_append(rval)
root.after(10,lambda:root.destroy())
root.mainloop()