import socket
from encryption_utils import encrypt_message, decrypt_message
import threading
import ssl
import os
from protocol import send_json, recv_json
from encryption_utils import generate_key

HOST = "0.0.0.0"
PORT = 5000

clients = {}       # socket -> username
user_sockets = {}  # username -> socket
rooms = {}         # room -> list of sockets
room_message_sequence = {}  # NEW: track ordering per room
lock = threading.Lock()


# Broadcast message to all users in a room
def broadcast_room(room, message, exclude=None):
    if room in rooms:
        for client in list(rooms[room]):  # safe iteration copy
            if client != exclude:
                try:
                    send_json(client, message)
                except Exception as e:
                    print("Broadcast failed:", e)
                    remove_client(client)


# Remove disconnected client safely
def remove_client(client):
    with lock:
        username = clients.get(client)

        if username:
            print(f"{username} disconnected")

            if username in user_sockets:
                del user_sockets[username]

            del clients[client]

            for room_name, room_clients in rooms.items():
                if client in room_clients:
                    room_clients.remove(client)

                    broadcast_room(room_name, {
                        "type": "info",
                        "message": f"{username} left the room"
                    })

        try:
            client.close()
        except:
            pass


# Handle each client connection
def handle_client(client):
    while True:
        try:
            try:
                data = recv_json(client)
            except Exception:
                print("Invalid packet received. Closing connection.")
                break

            if not data:
                print("Client disconnected unexpectedly")
                break

            msg_type = data.get("type")
            print("Received type:", msg_type)

            # JOIN ROOM
            if msg_type == "join":
                username = data["username"]
                room = data["room"]

                with lock:
                    if username in user_sockets:
                        send_json(client, {
                            "type": "info",
                            "message": "Username already taken. Try another."
                        })
                        continue

                    clients[client] = username
                    user_sockets[username] = client

                    if room not in rooms:
                        rooms[room] = []
                        room_message_sequence[room] = 0  # NEW: initialize counter

                    rooms[room].append(client)

                send_json(client, {
                    "type": "info",
                    "message": f"Joined room {room}"
                })

                broadcast_room(room, {
                    "type": "info",
                    "message": f"{username} joined the room"
                }, exclude=client)

            # ROOM MESSAGE WITH ORDER GUARANTEE
            elif msg_type == "message":
                room = data["room"]
                username = clients.get(client)

                with lock:
                    room_message_sequence[room] += 1
                    sequence_number = room_message_sequence[room]

                log_entry = f"[ROOM {room}] MSG#{sequence_number} {username}: {data['content']}"

                print(log_entry)

                # Save ordering proof to file
                with open("message_order_log.txt", "a") as f:
                    f.write(log_entry + "\n")

                broadcast_room(room, {
                    "type": "message",
                    "sender": username,
                    "sequence": sequence_number,
                    "content": data["content"]
                })

            # PRIVATE MESSAGE
            elif msg_type == "private":
                to_user = data["to"]
                username = clients.get(client)

                if to_user in user_sockets:
                    send_json(user_sockets[to_user], {
                        "type": "private",
                        "from": username,
                        "content": data["content"]
                    })

            # FILE TRANSFER
            elif msg_type == "file":
                filename = data["filename"]
                filesize = data["filesize"]
                room = data["room"]
                username = clients.get(client)

                broadcast_room(room, {
                    "type": "file",
                    "filename": filename,
                    "filesize": filesize,
                    "from": username
                }, exclude=client)

                remaining = filesize

                while remaining > 0:
                    chunk = client.recv(min(4096, remaining))
                    if not chunk:
                        break

                    remaining -= len(chunk)

                    for member in rooms.get(room, []):
                        if member != client:
                            try:
                                member.sendall(chunk)
                            except:
                                remove_client(member)

            # SECRET MESSAGE
            elif msg_type == "secret":
                to_user = data["to"]

                if to_user in user_sockets:
                    send_json(user_sockets[to_user], {
                        "type": "secret",
                        "from": clients.get(client),
                        "content": data["content"]
                    })

        except Exception as e:
            print("Client connection lost:", e)
            break

    remove_client(client)


# Start SSL server
def start_server():
    key = generate_key()

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)

    print("Server running with SSL...")

    while True:
        client, addr = server.accept()
        secure_client = context.wrap_socket(client, server_side=True)

        print(f"Connection from {addr}")

        threading.Thread(
            target=handle_client,
            args=(secure_client,),
            daemon=True
        ).start()


if __name__ == "__main__":
    start_server()