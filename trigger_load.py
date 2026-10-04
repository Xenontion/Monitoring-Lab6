import time
import requests

ORDER_URL = "http://localhost:8081/load/cpu"

print(">>> Надсилання навантаження на order-service для оновлення графіків у Portainer...")

for i in range(1, 15):
    try:
        res = requests.get(ORDER_URL, timeout=10)
        print(f"[{i}/14] CPU Stress batch triggered -> {res.status_code}")
    except Exception as e:
        print(f"[{i}/14] Error: {e}")
    time.sleep(0.5)

print("\n>>> Навантаження подано! Перевірте вкладку Stats у Portainer: http://localhost:9000")