import time
import threading
import requests
import pigpio
import wiegand
from tkinter import *
import IO_init

# ====================== CONFIG ======================
API_URL = "http://192.168.173.17/Api/Masterkey/get_info?Code="
ACCESS_TIMEOUT = 5  # seconds

# ====================== STATE ======================
STATE_IDLE = 0
STATE_UNLOCK = 1
STATE_WAIT_OPEN = 2
STATE_WAIT_CLOSE = 3

state = STATE_IDLE
last_card_id = None
last_access_time = 0

lock = threading.Lock()

# ====================== INIT IO ======================
IO_init.Init()
IO_init.SetIOOutput(IO_init.GPIO_LOCK, 1)
IO_init.SetIOOutput(IO_init.GPIO_Led, 0)

# ====================== WIEGAND ======================
def card_callback(bits, value):
    global last_card_id
    card_id = value & 0x1FFFF
    print(f"[CARD] {card_id}")

    with lock:
        last_card_id = card_id

def wiegand_thread():
    pi = pigpio.pi()
    if not pi.connected:
        raise RuntimeError("pigpiod not running")

    decoder = wiegand.decoder(pi, 20, 21, card_callback)

    try:
        while True:
            time.sleep(1)
    finally:
        decoder.cancel()
        pi.stop()

# ====================== API THREAD ======================
def api_thread():
    global state, last_card_id, last_access_time

    while True:
        with lock:
            card = last_card_id

        if card:
            try:
                print("[API] Checking card...")
                r = requests.get(API_URL + str(card), timeout=2).json()

                if r.get("Result") == "OK":
                    with lock:
                        state = STATE_UNLOCK
                        last_access_time = time.time()
                        print("[API] ACCESS GRANTED")
                else:
                    print("[API] ACCESS DENIED")
            except Exception as e:
                print("[API ERROR]", e)

            with lock:
                last_card_id = None

        time.sleep(0.1)

# ====================== LOCK CONTROL ======================
def lock_thread():
    global state

    while True:
        sensor = IO_init.GetIOStatus(IO_init.GPIO_Sensor)

        with lock:
            # timeout
            if state != STATE_IDLE and time.time() - last_access_time > ACCESS_TIMEOUT:
                state = STATE_IDLE

            if state == STATE_UNLOCK:
                IO_init.SetIOOutput(IO_init.GPIO_LOCK, 0)
                IO_init.SetIOOutput(IO_init.GPIO_Led, 1)
                state = STATE_WAIT_OPEN
                print("[LOCK] Relay ON")

            elif state == STATE_WAIT_OPEN and sensor == 1:
                IO_init.SetIOOutput(IO_init.GPIO_LOCK, 1)
                IO_init.SetIOOutput(IO_init.GPIO_Led, 0)
                state = STATE_WAIT_CLOSE
                print("[LOCK] Door opened")

            elif state == STATE_WAIT_CLOSE and sensor == 0:
                state = STATE_IDLE
                print("[LOCK] Door closed")

            elif state == STATE_IDLE:
                IO_init.SetIOOutput(IO_init.GPIO_LOCK, 1)
                IO_init.SetIOOutput(IO_init.GPIO_Led, 0)

        time.sleep(0.1)

# ====================== GUI ======================
def GUI():
    root = Tk()
    root.geometry("700x400")
    root.title("MasterKey Offline")

    status_text = StringVar(value="Scan card")

    lbl = Label(root, textvariable=status_text,
                font=("Arial", 22, "bold"))
    lbl.pack(pady=50)

    def update_gui():
        with lock:
            if state == STATE_IDLE:
                status_text.set("Scan card")
            elif state == STATE_WAIT_OPEN:
                status_text.set("Please open door")
            elif state == STATE_WAIT_CLOSE:
                status_text.set("Please close door")

        root.after(200, update_gui)

    update_gui()
    root.mainloop()

# ====================== MAIN ======================
if __name__ == "__main__":
    try:
        threading.Thread(target=wiegand_thread, daemon=True).start()
        threading.Thread(target=api_thread, daemon=True).start()
        threading.Thread(target=lock_thread, daemon=True).start()
        GUI()
    finally:
        print("Cleanup GPIO")
        IO_init.GPIO.cleanup()
``
