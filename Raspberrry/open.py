import pigpio
import wiegand
import time
import threading
import tkinter as tk
from tkinter import *
import IO_init

# ================== GLOBAL ==================
STATE_IDLE = 0
STATE_UNLOCK = 1
STATE_WAIT_OPEN = 2
STATE_WAIT_CLOSE = 3

state = STATE_IDLE
IDcard_code = 0
last_card_time = 0
ACCESS_TIMEOUT = 5  # giây

lock = threading.Lock()

# ================== INIT IO ==================
IO_init.Init()

# ================== WIEGAND ==================
def card_callback(bits, value):
    global state, IDcard_code, last_card_time

    card_id = value & 0x1FFFF
    print(f"[CARD] {card_id}")

    with lock:
        if card_id == 15819:
            IDcard_code = card_id
            state = STATE_UNLOCK
            last_card_time = time.time()
            print("[ACCESS GRANTED]")
        else:
            print("[ACCESS DENIED]")

def wiegand_thread():
    pi = pigpio.pi()
    if not pi.connected:
        raise RuntimeError("pigpiod not running")

    w = wiegand.decoder(pi, 20, 21, card_callback)
    try:
        while True:
            time.sleep(1)
    finally:
        w.cancel()
        pi.stop()

# ================== LOCK LOGIC ==================
def lock_control_thread():
    global state

    while True:
        sensor = IO_init.GetIOStatus(IO_init.GPIO_Sensor)

        with lock:
            # Timeout reset
            if state != STATE_IDLE and time.time() - last_card_time > ACCESS_TIMEOUT:
                state = STATE_IDLE

            if state == STATE_UNLOCK:
                IO_init.SetIOOutput(IO_init.GPIO_LOCK, 0)  # unlock
                state = STATE_WAIT_OPEN
                print("Relay ON")

            elif state == STATE_WAIT_OPEN and sensor == 1:
                IO_init.SetIOOutput(IO_init.GPIO_LOCK, 1)
                state = STATE_WAIT_CLOSE
                print("Door opened")

            elif state == STATE_WAIT_CLOSE and sensor == 0:
                state = STATE_IDLE
                print("Door closed")

            elif state == STATE_IDLE:
                IO_init.SetIOOutput(IO_init.GPIO_LOCK, 1)

        time.sleep(0.1)

# ================== GUI ==================
def GUI():
    root = Tk()
    root.title("MasterKey Offline")
    root.geometry("800x480")

    status = StringVar()
    status.set("Scan card")

    def update():
        with lock:
            if state == STATE_IDLE:
                status.set("Scan card")
            elif state == STATE_WAIT_OPEN:
                status.set("Please open door")
            elif state == STATE_WAIT_CLOSE:
                status.set("Please close door")

        root.after(200, update)

    Label(root, textvariable=status, font=("Arial", 20)).pack(pady=40)
    update()
    root.mainloop()

# ================== MAIN ==================
if __name__ == "__main__":
    threading.Thread(target=wiegand_thread, daemon=True).start()
    threading.Thread(target=lock_control_thread, daemon=True).start()
    GUI()
