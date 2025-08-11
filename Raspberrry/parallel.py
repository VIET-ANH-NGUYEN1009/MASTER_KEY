'''
#   Hoan thanh build cac function giong nhu cua ban Arduino
#   Dieu chinh Cau lenh ket noi voi API  --> Thay doi chuoi string nhan tu API
#       --> xu li chuoi string do
#
'''

import wiegand
import time
import pigpio as gpio
import requests
import threading
import IO_init
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox, Message
from _tkinter import TclError
import json
from multiprocessing import Process


""" --------------------global variable ----------------"""

dem =0
GPIO_Sensor_ON = False
GPIO_LOCK_ON = False
GPIO_LOCK_status = False
chuoi = None
id = None
wiegandData = 0
w = None
pi=None
timer = 0
serial_chuoi = None
chuoi2 = None
IO_init.Init()


"""---------------main-----------------------"""
def main():
    global chuoi2
    global chuoi
    global led_alarm
    global LOCK_event_handle, dem_cuamo, dem, GPIO_LOCK_status, LOCK_event_detect
    
    
    dem =0
    GPIO_Sensor_ON = False
    GPIO_LOCK_ON = False
    GPIO_LOCK_status = False
    chuoi = None
    id = None
    wiegandData = 0
    w = None
    pi=None
    timer = 0
    serial_chuoi = None
    chuoi2 = None
    IO_init.Init()


    #-------------------------RFID HANDLE-----------------------------------------

    def callback(bits, value):  # in ra code cua ID card
        global chuoi
        global IDcard_code
        global serial_chuoi
        global chuoi2
        try:
            print("bits={} value={}".format(bits, (value)))

            IDcard_code = int(bin(value)[-17:-1], 2)
            print(int(bin(value)[-17:-1], 2))     
            url='http://192.168.173.17/Api/Masterkey/get_info?Code='+ str(IDcard_code)
            print(url)
            response = requests.get(url, timeout=(1,4)).text
            chuoi = response
            chuoi2 = chuoi
            print("chuoi nhan duoc: |", chuoi)
            
        except:
            chuoi = None
            print("Khong connect duoc toi Api")

    # Read data from RFID
    def readWiegand():
         global w,pi
         import pigpio
         import wiegand
         pi = pigpio.pi()
         w = wiegand.decoder(pi, 20, 21, callback)
         # w.cancel()

    def LOCK_event_detect():
        global GPIO_LOCK_status
        if chuoi == None:
            #pass
             GPIO_LOCK_status = False
        elif chuoi == "NG":
            GPIO_LOCK_status = False
         # elif chuoi == "{NG}":
         #     GPIO_LOCK_status = True
         # elif   chuoi == " {OK}":
        elif chuoi == "OK":
            GPIO_LOCK_status = True
        else:
            GPIO_LOCK_status = False

            
    def count_cuamo():
        global dem_cuamo
        global dem
        dem_cuamo = dem_cuamo - 1
        print("dem cua mo: " , dem_cuamo)
        if dem_cuamo == 0:
            print("Activate nhung khong mo cua ")
            dem = 2
            chuoi = None
        
    def LOCK_event_handle():
        global dem_cuamo
        global dem
        global chuoi
        global GPIO_LOCK_status
        
        

        if  GPIO_LOCK_status == True and IO_init.GetIOStatus(IO_init.GPIO_Sensor)  == 0 and dem == 0:         # cua dong va co tin hieu mo cua
            IO_init.SetIOOutput(IO_init.GPIO_LOCK,0)
            dem = 1
            dem_cuamo = 50
            print("state 1")

            # Activate relay
        elif GPIO_LOCK_status == True and  IO_init.GetIOStatus(IO_init.GPIO_Sensor) == 0 and dem == 1:        # kich len nhung chua co tin hieu mo cua
            #IO_init.SetIOOutput(IO_init.GPIO_LOCK,0)
            #dem_cuamo = dem_cuamo - 1
            #if dem_cuamo == 0:
                #print("dem cua mo: " , dem_cuamo)
                #chuoi = None
            count_cuamo()
            print("state 2")
            
        elif GPIO_LOCK_status == True and  IO_init.GetIOStatus(IO_init.GPIO_Sensor) == 1 and dem == 1:        # cua mo
            dem = 2
            IO_init.SetIOOutput(IO_init.GPIO_LOCK,1)
            print("state 3")
            GPIO_LOCK_status = False
        elif GPIO_LOCK_status == True and dem == 2 and IO_init.GetIOStatus(IO_init.GPIO_Sensor)  == False:               # cua mo roi, lai dong
            dem = 0
            chuoi = None
            GPIO_LOCK_status = False
            IO_init.SetIOOutput(IO_init.GPIO_LOCK,1)
            print("state 4")
            
        elif GPIO_LOCK_status == False:
            dem = 0
            chuoi = None
            IO_init.SetIOOutput(IO_init.GPIO_LOCK,1)
        elif GPIO_LOCK_status == False :
            dem = 0
            chuoi = None
            IO_init.SetIOOutput(IO_init.GPIO_LOCK,1)     
        else:
            dem = 0
            chuoi = None
            IO_init.SetIOOutput(IO_init.GPIO_LOCK,1)


    try:
        send = readWiegand()
        IO_init.SetIOOutput(IO_init.GPIO_Led,1)
        time.sleep(1)
        IO_init.SetIOOutput(IO_init.GPIO_Led,0)
        time.sleep(1)
        IO_init.SetIOOutput(IO_init.GPIO_Led,1)
        time.sleep(1)
        IO_init.SetIOOutput(IO_init.GPIO_Led,0)
        time.sleep(1)
        IO_init.SetIOOutput(IO_init.GPIO_Led,1)
        time.sleep(1)
        IO_init.SetIOOutput(IO_init.GPIO_Led,0)
        time.sleep(1)            
      
        while True:
            if (IO_init.GetIOStatus(18)==0):       
                    # print("vong lap")
                if(IO_init.GetIOStatus(15) == 0):
                    GPIO_Sensor_ON = False

                LOCK_event_detect()
                LOCK_event_handle()
            
            
                
                print("----------------DEBUG---------------------")
                print(IO_init.GetIOStatus(IO_init.GPIO_Sensor))  # Sensor
                print(IO_init.GetIOStatus(IO_init.GPIO_Led))  # Lock
                    #print(dem)
                    #print(GPIO_LOCK_status)
                    #print(GPIO_Sensor_ON)
    ##                time.sleep(1)
                if chuoi != None and chuoi == chuoi2:
                        #time.sleep(0.2)
                    chuoi2 = None

                                                      
                print(str(chuoi2))
                print(str(chuoi))
                time.sleep(1)
            elif(IO_init.GetIOStatus(18)==1):
                IO_init.SetIOOutput(IO_init.GPIO_LOCK,0)
                time.sleep(15)
                
    except:
        print("GPIO reset")
    finally:
        print("Hoan thanh")
        IDcard_code = 0
        IO_init.GPIO.cleanup()
        w.cancel()
        pi.stop()
        

"""
-------------GUI--------------------

"""
def GUI():
    global e, e1, e2, lastplace
    global IDcard_code
    global dem_cuamo
    global dem
    root = Tk()
    root.title("   ")
    root["bg"]= "#b0c4de"
    root.geometry("800x480")

    """ -----------------------------functon---------------------------------"""
               
    def bold(self):
        global e, e1, history, lastplace
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
    
    def approval_show():
        global lastplace
        e.delete("1.0", END)
        lastplace = e.index("1.0")
        e.tag_config("hide", elide =1)
        e.tag_config("bold", font = "Courier 10 bold")
        try:
            url1 = "http://192.168.173.17/Api/Masterkey/Waiting_Unlock?Location=TL-2nd-floor"
            response1 = requests.get(url1, timeout=10).text
            a = json.loads(response1)
            for i in range(len(a)):
                e.insert(END, "\n" +"[B] Name: [/B]"+ a[i]["Borrower_Name"] +" [B] Code: [/B]"+ a[i]["Borrower_Code"] +" [B] Dept: [/B]"+ a[i]["Dept"]+" \n[B] Equip: [/B]" + a[i]["Equip_Name"]+" \n[B] Approval Time: [/B]" + a[i]["Approval_time"] + "\n ---------------------------------------------------- ")
                bold(e)
            e.after(4000, approval_show)
        except:
            print("Something gonna wrong!")
            e.after(4000, approval_show)

            
    
    def history_show():
        global lastplace
        hist.delete("1.0", END)
        lastplace = hist.index("1.0")
        hist.tag_config("hide", elide =1)
        hist.tag_config("bold", font = "Courier 10 bold")
        try:
            url2 = "http://192.168.173.17/Api/Masterkey/Masterkey_History?Location=TL-2nd-floor"
            response2 = requests.get(url2, timeout=10).text
            a = json.loads(response2)
            for i in range(len(a)):
                hist.insert(END, "\n" +"[B]Name: [/B]"+ a[i]["Borrower_Name"] +" [B]Dept: [/B]"+ a[i]["Dept"]+" \n[B]Equip: [/B]" + a[i]["Equip_Name"]+" \n[B]KEY:   [/B]" + a[i]["Cabinet"]+ " \n[B]Time: [/B]" + a[i]["Masterkey_time"] + "\n------------------------------------- ")
                bold(hist)
            hist.after(5000, history_show)
        except:
            print("Something gonna wrong!")
            hist.after(5000, history_show)

        
    def change_color():
        global e2
        if IO_init.GetIOStatus(IO_init.GPIO_Sensor) == 0:
            canvas.itemconfig(arc, fill ="red" )
        else:
            canvas.itemconfig(arc, fill ="green" )
        canvas.after(100, change_color)
                    
            
    def click_start():
        e1.delete("1.0", END)
        e1.insert("1.0", "\n WELCOME TO MASTERKEY!")
        if IO_init.GetIOStatus(IO_init.GPIO_Sensor) == 0:
            e2.delete("1.0", END)
            e2.insert("1.0", "Door closed! \nPlease check your request status before opening....")
        else:
            e2.delete("1.0", END)
            e2.insert("1.0", "Xin chao...!\nTake your key and please close after using!")
        e2.after(1000, click_start) 
    """
    def callback(bits, value):  # in ra code cua ID card
        global IDcard_code
        global serial_chuoi
        try:
            IDcard_code = int(bin(value)[-17:-1], 2)
            print(int(bin(value)[-17:-1], 2))     
            url='http://192.168.173.17/Api/Masterkey/get_info?Code='+ str(IDcard_code)
            #print(url)
            response = requests.get(url, timeout=(1,4)).text
 
        except:
            response = None

    # Read data from RFID
    def readWiegand():
         global w,pi
         import pigpio
         import wiegand
         pi = pigpio.pi()
         w = wiegand.decoder(pi, 20, 21, callback)
         # w.cancel()    
    def message_faile():
        #try:
            send = readWiegand()
            if (response  == "NG"):
                messagebox.showerror(title=None, message="You can´t access..!\nPls check your request status.")
            else:
                messagebox.showinfo(title=None, message = "access successfully!")
        #except:
         #   print(" ")
        
            e.after(100, message_faile)
    """
        
    """ -------------------label control ------------------"""
    label_main = Label(root, text = "MasterKey", font = ("Arial bold", 15), fg = "green", bg = "#b0c4de")
    label_main.grid(row=0, column = 0, columnspan=4)
    
    label_canon = Label(root, text = "Canon VietNam", font = "Courier 8 bold italic", fg = "red", bg= "#b0c4de")
    label_canon.grid(row=3, column = 0, sticky= (tk.N, tk.W, tk.S))
    
    label_designer = Label(root, text = "DEV by TIM Advanced Group! (.*<>*.)(^.^) ", font = ("Arial", 8), fg = "blue", bg = "#b0c4de")
    label_designer.grid(row = 3, column = 1, columnspan = 3, sticky= (tk.N, tk.E, tk.S))
    
    """ -------------------frame control-----------------------------"""
    
    frame_GUI_status = LabelFrame(root, text = "GUI Status", font =("Arial", 9), bg = "#b0c4de")
    frame_GUI_status.grid(row=1, column = 0, sticky = (tk.N, tk.W, tk.S))
    
    frame_door_waiting = LabelFrame(root, text = "Door Status", font =("Arial", 9), bg = "#b0c4de")
    frame_door_waiting.grid(row=1, column = 1,columnspan=2, sticky = (tk.N, tk.W, tk.S))
    
    frame_door_status = LabelFrame(root, text = " ", font =("Arial", 7), bg = "#b0c4de")
    frame_door_status.grid(row=1, column = 3, sticky = (tk.N, tk.W, tk.S))
    
    frame_approval_list = LabelFrame(root, text = "Waiting get key list", font =("Arial", 9), bg = "#b0c4de")
    frame_approval_list.grid(row=2, column = 0,columnspan=2, sticky = (tk.N, tk.W, tk.S, tk.E))

    frame_history_list = LabelFrame(root, text = "History List", font =("Arial", 9), bg = "#b0c4de")
    frame_history_list.grid(row=2, column = 2, columnspan=2, sticky = (tk.N, tk.W, tk.S, tk.E))

    
    """ -------------------component in frame door status -------------------"""
    canvas = tk.Canvas(frame_door_status, height = 60, width = 60, bg = "#b0c4de")
    canvas.pack()
    arc = canvas.create_arc(1,1,60,60, start = 0, extent = 359 , fill = "red")
    change_color()


    """------------------component in frame show approval list-----------------------"""
    e = Text(frame_approval_list, width = 52, height = 19)
    e.grid(row = 0, column =0, sticky=(N, W, E, S))

    ybar = ttk.Scrollbar(frame_approval_list, orient =VERTICAL, command = e.yview)
    ybar.grid(row= 0, column = 1, sticky=(N, W, E, S))
    #xbar = ttk.Scrollbar(frame_2, orient =HORIZONTAL, command = e.xview)
    #xbar.grid(row= 1, column = 0, columnspan = 2, sticky=(N, W, E, S))
    e["yscrollcommand"]= ybar.set
    #e["xscrollcommand"]= xbar.set
    
    """---------------------component in history frame--------------------"""

    hist = Text(frame_history_list, width = 40 , height = 19)
    hist.grid(row = 0, column =0, sticky=(N, W, E, S))

    ybar = ttk.Scrollbar(frame_history_list, orient =VERTICAL, command = hist.yview)
    ybar.grid(row= 0, column = 1, sticky=(N, W, E, S))
    #xbar = ttk.Scrollbar(frame_2, orient =HORIZONTAL, command = e.xview)
    #xbar.grid(row= 1, column = 0, columnspan = 2, sticky=(N, W, E, S))
    hist["yscrollcommand"]= ybar.set
    #e["xscrollcommand"]= xbar.set    
    
    """------------------component in frame GUI status--------------------"""
    e1 = Text(frame_GUI_status, height = 3, width = 25, font = "Arial 13 bold", fg = "#50c78f")
    e1.pack()

    """ -----------------component in Frame status door--------------------"""
    e2 = Text(frame_door_waiting, height = 3, width = 44, font = ("Arial Italic", 12))
    e2.pack()
    
    """---------Auto run-------------"""
    click_start()
    approval_show()
    history_show()
    #message_faile()
    root.mainloop()
    



#---------------------------------------------MAIN-------------------------------------------

if __name__ == "__main__":
    p1 = Process(target = main)
    p1.start()
    p2 = Process(target = GUI)
    p2.start()
    p1.join()
    p2.join()
