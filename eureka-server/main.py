import time
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Eureka Server Mock")

# Реєстр сервісів: {app_name: {instance_id: {...}}}
registry = {}

class InstanceInfo(BaseModel):
    instance_id: str
    app_name: str
    ip_addr: str
    port: int
    status: str = "UP"

@app.post("/eureka/apps/{app_name}")
def register(app_name: str, info: InstanceInfo):
    app_key = app_name.upper()
    if app_key not in registry:
        registry[app_key] = {}
    registry[app_key][info.instance_id] = {
        "instance_id": info.instance_id,
        "ip": info.ip_addr,
        "port": info.port,
        "status": info.status,
        "last_heartbeat": time.time()
    }
    return {"message": "registered"}

@app.put("/eureka/apps/{app_name}/{instance_id}")
def heartbeat(app_name: str, instance_id: str):
    app_key = app_name.upper()
    if app_key in registry and instance_id in registry[app_key]:
        registry[app_key][instance_id]["last_heartbeat"] = time.time()
        registry[app_key][instance_id]["status"] = "UP"
        return {"status": "renewed"}
    return {"error": "not found"}

@app.delete("/eureka/apps/{app_name}/{instance_id}")
def deregister(app_name: str, instance_id: str):
    app_key = app_name.upper()
    if app_key in registry and instance_id in registry[app_key]:
        del registry[app_key][instance_id]
        return {"message": "deregistered"}
    return {"error": "not found"}

@app.get("/", response_class=HTMLResponse)
def dashboard():
    now = time.time()
    rows = ""
    for app_name, instances in registry.items():
        for inst_id, data in instances.items():
            # Якщо heartbeat не надходив понад 15 сек — статус стає DOWN
            status = "UP" if (now - data["last_heartbeat"]) < 15 else "DOWN"
            color = "#28a745" if status == "UP" else "#dc3545"
            rows += f"""
            <tr>
                <td><strong>{app_name}</strong></td>
                <td>{inst_id}</td>
                <td>{data['ip']}:{data['port']}</td>
                <td style="color: {color}; font-weight: bold;">{status}</td>
                <td>{int(now - data['last_heartbeat'])}s ago</td>
            </tr>
            """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Eureka Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 30px; background: #f8f9fa; }}
            h1 {{ color: #212529; border-bottom: 2px solid #6c757d; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background: white; }}
            th, td {{ border: 1px solid #dee2e6; padding: 12px; text-align: left; }}
            th {{ background: #343a40; color: white; }}
            tr:nth-child(even) {{ background: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>Spring Cloud / Eureka Discovery Dashboard</h1>
        <p><strong>System Status:</strong> Environment: Production-Test | Registered Applications: {len(registry)}</p>
        <table>
            <thead>
                <tr>
                    <th>Application</th>
                    <th>Instance ID</th>
                    <th>Endpoint</th>
                    <th>Status</th>
                    <th>Last Heartbeat</th>
                </tr>
            </thead>
            <tbody>
                {rows if rows else '<tr><td colspan="5">No instances currently registered</td></tr>'}
            </tbody>
        </table>
    </body>
    </html>
    """
    return html