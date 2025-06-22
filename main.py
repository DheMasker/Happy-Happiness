import websocket
import time

# Konfigurasi WebSocket
server = "104.22.5.240"
port = 443
path = "/trhup"
sni = "rs1.x-tls.my.id"

# URL untuk koneksi WebSocket
url = f"wss://{server}:{port}{path}"

# Mengukur latency
start_time = time.time()

try:
    # Membuat koneksi WebSocket
    ws = websocket.create_connection(url, header={"Host": sni})
    latency = time.time() - start_time
    ws.close()
    print("Proxy aktif, Latency:", latency, "detik")
except Exception as e:
    print("Proxy tidak aktif:", e)
