import socket
import threading
import ssl
import os
from protocol import send_json, recv_json
from encryption_utils import encrypt_message, decrypt_message, set_key

HOST = "172.20.10.5"   # Change to server IP if needed
PORT = 5000


def receive_messages(sock):
    while True:
        try:
            data = recv_json(sock)

            if not data:
                print("Disconnected from server.")
                break

            msg_type = data.get("type")

            if msg_type == "message":
                print(f"[{data['sender']}]: {data['content']}")

            elif msg_type == "private":
                print(f"[PRIVATE from {data['from']}]: {data['content']}")

            elif msg_type == "secret":
                decrypted = decrypt_message(data["content"])
                print(f"[SECRET from {data['from']}]: {decrypted}")

            elif msg_type == "info":
                print(f"[INFO]: {data['message']}")

            elif msg_type == "file":
                filename = data["filename"]
                filesize = data["filesize"]

                os.makedirs("received_files", exist_ok=True)

                filepath = os.path.join("received_files", filename)

                remaining = filesize

                with open(filepath, "wb") as f:
                    while remaining > 0:
                        chunk = sock.recv(min(4096, remaining))
                        if not chunk:
                            break
                        f.write(chunk)
                        remaining -= len(chunk)

                print(f"[FILE RECEIVED]: {filepath}")

        except Exception as e:
            print("Connection closed:", e)
            break


def start_client():
    # Encryption key (must match server key)
    key = b'7S357ZthynRtFopFFKIton9Ke1PzhJkIMwK7M-Rjvy4='
    set_key(key)

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    secure_sock = context.wrap_socket(sock)

    secure_sock.connect((HOST, PORT))

    print("Connected to server.")

    threading.Thread(
        target=receive_messages,
        args=(secure_sock,),
        daemon=True
    ).start()

    username = input("Enter username: ")
    room = input("Enter room: ")

    send_json(secure_sock, {
        "type": "join",
        "username": username,
        "room": room
    })

    while True:
        try:
            msg = input()

            if msg.startswith("/private"):
                parts = msg.split(" ", 2)

                if len(parts) < 3:
                    print("Usage: /private username message")
                    continue

                _, to_user, content = parts

                send_json(secure_sock, {
                    "type": "private",
                    "to": to_user,
                    "content": content
                })

            elif msg.startswith("/secret"):
                parts = msg.split(" ", 2)

                if len(parts) < 3:
                    print("Usage: /secret username message")
                    continue

                _, to_user, content = parts

                encrypted = encrypt_message(content)

                send_json(secure_sock, {
                    "type": "secret",
                    "to": to_user,
                    "content": encrypted
                })

            elif msg.startswith("/file"):
                parts = msg.split(" ", 1)

                if len(parts) < 2:
                    print("Usage: /file filename")
                    continue

                filepath = parts[1]

                if not os.path.exists(filepath):
                    print("File not found.")
                    continue

                filesize = os.path.getsize(filepath)
                filename = os.path.basename(filepath)

                send_json(secure_sock, {
                    "type": "file",
                    "filename": filename,
                    "filesize": filesize,
                    "room": room
                })

                with open(filepath, "rb") as f:
                    while True:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        secure_sock.sendall(chunk)

                print(f"[FILE SENT]: {filename}")

            else:
                send_json(secure_sock, {
                    "type": "message",
                    "room": room,
                    "content": msg
                })

        except KeyboardInterrupt:
            print("\nDisconnected.")
            secure_sock.close()
            break


if __name__ == "__main__":
    start_client()