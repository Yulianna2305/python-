import socket
import threading
import json

HOST = "0.0.0.0"
PORT = 5000

clients = {}          
positions = {}        

def broadcast(data, exclude_client=None):
    message = json.dumps(data).encode("utf-8")
    for client in clients:
        if client != exclude_client:
            try:
                client.send(message + b"\n")
            except:
                pass

def handle_client(conn):
    try:
        username = conn.recv(1024).decode("utf-8").strip()
        clients[conn] = username

        print(f"[JOIN] {username} підключився.")

        # Сповіщаємо інших
        broadcast({"type": "message",
                   "user": "SERVER",
                   "text": f"{username} підключився."},
                  exclude_client=conn)

        while True:
            data = conn.recv(1024)
            if not data:
                break

            for raw in data.splitlines():
                try:
                    msg = json.loads(raw.decode("utf-8"))
                except:
                    continue

                if msg["type"] == "position":
                    positions[username] = (msg["x"], msg["y"])
                    broadcast(msg, exclude_client=conn)

                if msg["type"] == "message":
                    broadcast(msg, exclude_client=conn)

    finally:
        username = clients.get(conn, "unknown")
        print(f"[LEAVE] {username} відключився.")

        clients.pop(conn, None)
        positions.pop(username, None)

        broadcast({"type": "message",
                   "user": "SERVER",
                   "text": f"{username} відключився."})

        conn.close()

def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[SERVER] Запущено на {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

if __name__ == "__main__":
    start()