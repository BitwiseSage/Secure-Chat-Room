import socket
import threading
import ssl
import os
from protocol import send_json, recv_json
from encryption_utils import encrypt_message, decrypt_message, set_key

HOST = "172.20.10.2"   # e.g. "10.25.69.26"
PORT = 5000

def receive_messages(sock):
    while True:
        try:
            data = recv_json(sock)
            if not data:
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
                filename = "received_files/" + data["filename"]
                filesize = data["filesize"]
                remaining = filesize

                with open(filename, "wb") as f:
                    while remaining > 0:
                        chunk = sock.recv(min(4096, remaining))
                        f.write(chunk)
                        remaining -= len(chunk)

                print(f"[FILE RECEIVED]: {filename}")

        except:
            break


def start_client():
    # SSL setup
    key =   b'oGk8-xGWT0PhL0ek9rhQ1xgGjkVaawX8EhAHfy5bHmQ='
    set_key(key)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    secure_sock = context.wrap_socket(raw_sock)
    secure_sock.connect((HOST, PORT))

    threading.Thread(target=receive_messages, args=(secure_sock,), daemon=True).start()

    username = input("Enter username: ")
    room = input("Enter room: ")

    send_json(secure_sock, {
        "type": "join",
        "username": username,
        "room": room
    })

    while True:
        msg = input()

        # Private message
        if msg.startswith("/private"):
            _, to_user, content = msg.split(" ", 2)
            send_json(secure_sock, {
                "type": "private",
                "to": to_user,
                "content": content
            })

        # Secret encrypted message
        elif msg.startswith("/secret"):
            _, to_user, content = msg.split(" ", 2)
            encrypted_content = encrypt_message(content)

            send_json(secure_sock, {
                "type": "secret",
                "to": to_user,
                "content": encrypted_content
            })

        # File sending
        elif msg.startswith("/file"):
            _, filepath = msg.split(" ", 1)
            filesize = os.path.getsize(filepath)
            filename = os.path.basename(filepath)

            send_json(secure_sock, {
                "type": "file",
                "filename": filename,
                "filesize": filesize,
                "room": room
            })

            with open(filepath, "rb") as f:
                while chunk := f.read(4096):
                    secure_sock.sendall(chunk)

        # Normal room message
        else:
            send_json(secure_sock, {
                "type": "message",
                "room": room,
                "content": msg
            })


if __name__ == "__main__":
    start_client()