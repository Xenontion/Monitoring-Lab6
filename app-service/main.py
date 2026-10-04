import os
import time
import socket
import threading
import requests
from fastapi import FastAPI

app = FastAPI()

APP_NAME = os.getenv("APP_NAME", "ORDER-SERVICE")
APP_PORT = int(os.getenv("APP_PORT", "8081"))
EUREKA_URL = os.getenv("EUREKA_URL", "http://eureka-server:8761")
INSTANCE_ID = f"{APP_NAME}-{socket.gethostname()}"

def eureka_worker():
    time.sleep(3)
    reg_data = {
        "instance_id": INSTANCE_ID,
        "app_name": APP_NAME,
        "ip_addr": socket.gethostbyname(socket.gethostname()),
        "port": APP_PORT,
        "status": "UP"
    }
    try:
        requests.post(f"{EUREKA_URL}/eureka/apps/{APP_NAME}", json=reg_data, timeout=3)
    except Exception as e:
        print(f"Registration error: {e}")

    while True:
        try:
            requests.put(f"{EUREKA_URL}/eureka/apps/{APP_NAME}/{INSTANCE_ID}", timeout=3)
            print(f"[{APP_NAME}] Heartbeat sent")
        except Exception as e:
            print(f"Heartbeat failed: {e}")
        time.sleep(5)

@app.on_event("startup")
def startup_event():
    threading.Thread(target=eureka_worker, daemon=True).start()

@app.get("/health")
def health():
    return {"status": "UP", "instance": INSTANCE_ID}

@app.get("/load/cpu")
def cpu_load():
    # Штучне навантаження на CPU на 4 секунди для графіків Portainer
    start = time.time()
    while time.time() - start < 4:
        _ = 99999 * 99999
    return {"message": "CPU stress completed"}