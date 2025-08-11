import wiegand
import time
import pigpio as gpio
import requests
import threading
import IO_init
import tkinter as tk
from tkinter import *
from tkinter import ttk
import json

root = Tk()

e =Text(root)
e.pack(side = LEFT)
e1 = Text(root)
e1.pack(side = RIGHT)
lastplace = e1.index("1.0")
e1.tag_config("hide", elide =1)
e1.tag_config("bold", font = "Courier 10 bold")

def bold(self):
    global lastplace
    nextplace = self.search("[B]", lastplace, "end")
    if nextplace:
        boldon = nextplace + " +3c"
        self.tag_add("hide", nextplace, boldon)
        boldoff = self.search("[/B]", boldon, "end")
        if boldoff:
            self.tag_add("bold", boldon, boldoff)
            codoff = boldoff + " +4c"
            self.tag_add("hide", boldoff, codoff)
        lastplace = codoff
        bold(self)
    else:
        return


def get_api():
    global response
    e.insert("1.0", response)
    
def devide_json():
    global response
    global e1, lastplace
    lastplace = e1.index("1.0")
    e1.tag_config("hide", elide =1)
    e1.tag_config("bold", font = "Courier 10 bold")
    e1.delete("1.0", "end")
    a = json.loads(response)
    for i in range(len(a)):
        e1.insert(END, "\n" +"[B] Name : [/B]"+ a[i]["Borrower_Name"] +"     [B] Code : [/B]"+ a[i]["Borrower_Code"] +"     [B] Dept : [/B]"+ a[i]["Dept"]+" \n[B] Equip : [/B]" + a[i]["Equip_Name"]+" \n[B] Approval Time : [/B]" + a[i]["Approval_time"] + "\n *            *                * ")
        bold(e1)
    e1.after(1000, devide_json)
        # e1.insert("1.0", custom_1_get["Borrower_Code"])
    

url = "http://192.168.173.17/Api/Masterkey/Waiting_Unlock?Location=TL-2nd-floor"
response = requests.get(url, timeout=10).text

button =Button(root, text ="Get API",command = get_api).pack()
button1 =Button(root, text ="devide json",command = devide_json).pack()

root.mainloop()