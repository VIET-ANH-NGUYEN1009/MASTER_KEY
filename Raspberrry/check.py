#_*_ coding: utf-8 _*_

import serial
import time

############################
seri = serial.Serial(
    port = "/dev/ttyACM0",
    baudrate = 9600,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout = 1
)

print("Sending:...")
########################################
def handle(return_str):
    return_str_split = return_str.split(',')
    print(return_str_split)
    return return_str_split
########################################
def receive():
    #time.sleep(2)  #delay 1s de arduino gui OK_name va Pi nhan duoc.
    print(seri.inWaiting())
    status = seri.readline()
    print(status)
    data = status.decode()
    print(data)
    OK = data.split()
    print(OK)
    return OK
########################################
def Send(infor):
    #print('send')
    try:
##        time.sleep(1)
        print('bat dau gui')
        seri.write(infor.encode())
        seri.flush()
##        time.sleep(1)
        #print('test done.')
        
    except AttributeError:
        print('Chua gui duoc')
    #pass          
    #print('Gui chuoi OK.' + chuoi + ',')
########################################
def CardCode():
    card = '35530'  #Function tra ve Cardcode cua user
    return card
########################################
if __name__ == '__main__':
    pass