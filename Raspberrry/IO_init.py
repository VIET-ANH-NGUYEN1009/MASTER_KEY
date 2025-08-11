import RPi.GPIO as GPIO

GPIO_Sensor = 15
GPIO_LOCK = 5
GPIO_Led = 22
GPIO_sensor2 = 18
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
# remember, a program doesn't necessarily exit at the last line!

def Init():                                                      # void setup
    global GPIO_Sensor,GPIO_LOCK,GPIO_Led, GPIO_sensor2
    GPIO.setup(GPIO_Sensor, GPIO.IN,pull_up_down = GPIO.PUD_UP)
    GPIO.setup(GPIO_LOCK, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(GPIO_Led, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(GPIO_sensor2, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def GetIOStatus(GPIO_Name):                                     # digitalRead
    return GPIO.input(GPIO_Name)

def SetIOOutput(GPIO_Name,bool):                                # digitalWrite
    GPIO.output(GPIO_Name,bool)

def EvenIO(channel, edge, callback, bouncetime):                # Extenal interrupt
    GPIO.add_event_detect (channel, edge, callback, bouncetime)
