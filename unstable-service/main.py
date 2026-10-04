import os
import sys
import time
import socket
import threading
import requests
from fastapi import FastAPI

app = FastAPI()

APP_NAME = os.getenv("APP_NAME", "UNSTABLE-WORKER")
APP_PORT = int(os.getenv("APP_PORT", "8085"))
EUREKA_URL = os.getenv("EUREKA_URL", "http://eureka-server:8761")
INSTANCE_ID = f"{APP_NAME}-{socket.gethostname()}"

def life_cycle_simulator():
    time.sleep(4)
    reg_data = {
        "instance_id": INSTANCE_ID,
        "app_name": APP_NAME,
        "ip_addr": socket.gethostbyname(socket.gethostname()),
        "port": APP_PORT,
        "status": "UP"
    }
    try:
        requests.post(f"{EUREKA_URL}/eureka/apps/{APP_NAME}", json=reg_data, timeout=3)
        print(f"[{APP_NAME}] Registered with Eureka")
    except Exception as e:
        print(f"Reg error: {e}")

    # Сервіс надсилає 2 heartbeat, після чого випадає з помилкою через 25 секунд
    for _ in range(2):
        time.sleep(6)
        try:
            requests.put(f"{EUREKA_URL}/eureka/apps/{APP_NAME}/{INSTANCE_ID}", timeout=3)
        except Exception:
            pass

    print(f"[{APP_NAME}] FATAL: OutOfMemoryError / Core dumped. Process killed!")
    time.sleep(2)
    os._exit(1)

@app.on_event("startup")
def startup():
    threading.Thread(target=life_cycle_simulator, daemon=True).start()

@app.get("/")
def root():
    return {"status": "CRITICAL_STATE"}