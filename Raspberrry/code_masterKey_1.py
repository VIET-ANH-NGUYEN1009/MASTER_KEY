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
        print(int(bin(value)[-17:-1], 2))     # code chinh xac cua ID card

                
       # url = 'http://192.168.191.58:8013/MasterKey/Get_Info?Code='+ str(IDcard_code)
        url='http://192.168.173.17/Api/Masterkey/get_info?Code='+ str(IDcard_code)
        print(url)
        response = requests.get(url, timeout=(1,4)).text
        #if chuoi.split('.')[0] == "0":
            #response = "{NG}"
            #chuoi = "{NG}"
        #else:
        chuoi = response
        chuoi2 = chuoi
        print("chuoi nhan duoc: |", chuoi)
        
        #check.Send(chuoi, IDcard_code)
        
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

#-------------------------SENSOR DETECT EVENT-----------------------------------------
# def OnEvenGPIO_Sensor(chanel):  # event change when sensor detect when open door
#     global GPIO_Sensor_ON
#     print('Sensor ON')
#     GPIO_Sensor_ON=True
#
#
# # detect when sensor close or not
# IO_init.EvenIO(IO_init.GPIO_Sensor,IO_init.GPIO.RISING,callback=OnEvenGPIO_Sensor,bouncetime=1000) # Falling la dong sensor lai
#--------------------------LOCK HANDLE-----------------------------------------

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
        IO_init.SetIOOutput(IO_init.GPIO_LOCK,0)
        print("state 3")
        GPIO_LOCK_status = False
    elif GPIO_LOCK_status == True and dem == 2 and IO_init.GetIOStatus(IO_init.GPIO_Sensor)  == False:               # cua mo roi, lai dong
        dem = 0
        chuoi = None
        GPIO_LOCK_status = False
        IO_init.SetIOOutput(IO_init.GPIO_LOCK,0)
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
        dem_cuamo = 10       


#--------------------------LED ALARM EVENT---------------------------------------
def led_alarm():
    global timer
    if IO_init.GetIOStatus(IO_init.GPIO_Sensor) == 1:
        timer = timer + 1
    elif IO_init.GetIOStatus(IO_init.GPIO_Sensor) == 0:
        timer = 0
        IO_init.SetIOOutput(IO_init.GPIO_Led,1)
    if timer > 20:
        timer = 21
    if timer == 21:
        IO_init.SetIOOutput(IO_init.GPIO_Led, 1-(IO_init.GetIOStatus(IO_init.GPIO_Led)))

#---------------------------------------------MAIN-------------------------------------------
if __name__ == "__main__":
    # while True:
        
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
                
                # print("vong lap")
                if(IO_init.GetIOStatus(15) == 0):
                    GPIO_Sensor_ON = False

                LOCK_event_detect()
                LOCK_event_handle()
                
                led_alarm()
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
                
        except:
            print("GPIO reset")
        finally:                    # if have bug so that make this Code run to except --> turn off the GPIO and reloop by Big "while"
             print("Hoan thanh")
             IDcard_code = 0
             IO_init.GPIO.cleanup()
             w.cancel()
             pi.stop()


