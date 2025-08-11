import IO_init as GPIO
from time import sleep

try:
    GPIO.Init()
    print("Khoi tao IO hoan tat")
except:
    print("Khoi tao bi loi")
def get_status():
    print("---------------------------Status--------------------")
    print("Sensor s Status",GPIO.GetIOStatus(GPIO.GPIO_Sensor))
    print("Lock s Status", GPIO.GetIOStatus(GPIO.GPIO_LOCK))
    print("Led s Status", GPIO.GetIOStatus(GPIO.GPIO_Led))
    print("Sensor2 s Status",GPIO.GetIOStatus(GPIO.GPIO_sensor2))

    sleep(1)

def check_Led():
    print("------------Led Control---------------")
    GPIO.SetIOOutput(GPIO.GPIO_Led,1)
    sleep(1)
    GPIO.SetIOOutput(GPIO.GPIO_Led,1)
    sleep(1)
def check_Lock():
    print("------------Lock Control-------------------")
    GPIO.SetIOOutput(GPIO.GPIO_LOCK,1)
    sleep(1)
    GPIO.SetIOOutput(GPIO.GPIO_LOCK,1)
    sleep(1)
while True:
    if (GPIO.GetIOStatus(18)==1):
        GPIO.SetIOOutput(GPIO.GPIO_LOCK,0)
    else:
        GPIO.SetIOOutput(GPIO.GPIO_LOCK,1)
    get_status()
    #check_Led()
    check_Led()
    
