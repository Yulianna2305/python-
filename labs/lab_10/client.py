import socket
import threading
import json

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

def listen(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break

            for raw in data.splitlines():
                try:
                    msg = json.loads(raw.decode("utf-8"))
                except:
                    continue

                if msg["type"] == "position":
                    print(f"[POS] {msg['user']}: ({msg['x']}, {msg['y']})")

                if msg["type"] == "message":
                    print(f"[{msg['user']}] {msg['text']}")

        except:
            break

def main():
    username = input("Введи ім'я користувача: ")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))

    sock.send((username + "\n").encode("utf-8"))

    threading.Thread(target=listen, args=(sock,), daemon=True).start()

    print("Команди:")
    print("/move x y  - надіслати координати")
    print("звичайний текст - повідомлення в чат\n")

    while True:
        msg = input()

        if msg.startswith("/move"):
            try:
                _, x, y = msg.split()
                data = {
                    "type": "position",
                    "user": username,
                    "x": float(x),
                    "y": float(y)
                }
                sock.send((json.dumps(data) + "\n").encode("utf-8"))
            except:
                print("Формат: /move 12.5 44.2")
            continue

        data = {
            "type": "message",
            "user": username,
            "text": msg
        }
        sock.send((json.dumps(data) + "\n").encode("utf-8"))

if __name__ == "__main__":
    main()