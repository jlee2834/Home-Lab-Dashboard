from flask import Flask, render_template
import psutil
import platform
import subprocess
from datetime import datetime

app = Flask(__name__)

PING_TARGETS = ["1.1.1.1", "8.8.8.8", "google.com"]

SERVICES = {
    "Proxmox": "https://YOUR_PROXMOX_IP:8006",
    "Router": "http://YOUR_ROUTER_IP",
    "NAS": "http://YOUR_NAS_IP",
}


def ping_host(host):
    command = ["ping", "-n", "1", host] if platform.system() == "Windows" else ["ping", "-c", "1", host]

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=5)
        return "Online" if result.returncode == 0 else "Offline"
    except Exception:
        return "Offline"


def get_system_stats():
    return {
        "hostname": platform.node(),
        "os": platform.system(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "ram_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
    }


def get_network_status():
    return [{"target": target, "status": ping_host(target)} for target in PING_TARGETS]


def get_service_status():
    results = []

    for name, url in SERVICES.items():
        host = url.replace("https://", "").replace("http://", "").split(":")[0].split("/")[0]
        results.append({
            "name": name,
            "url": url,
            "status": ping_host(host)
        })

    return results


@app.route("/")
def dashboard():
    return render_template(
        "dashboard.html",
        stats=get_system_stats(),
        network=get_network_status(),
        services=get_service_status(),
        generated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
