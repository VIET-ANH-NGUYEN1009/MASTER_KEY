import IO_init
from time import sleep

IO_init.Init()

while True:
    IO_init.SetIOOutput(23,1)
    sleep(1)
    IO_init.SetIOOutput(23,0)
    sleep(1)
