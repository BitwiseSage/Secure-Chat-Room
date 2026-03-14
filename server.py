import socket
import threading
import ssl
from protocol import send_json, recv_json

HOST = "0.0.0.0"
PORT = 5000

clients = {}
user_sockets = {}
rooms = {}
lock = threading.Lock()


def broadcast_room(room, message, exclude=None):

    if room in rooms:

        for client in rooms[room]:

            if client != exclude:

                try:
                    send_json(client, message)

                except:
                    remove_client(client)


def remove_client(client):

    with lock:

        username = clients.get(client)

        if username:

            print(f"{username} disconnected")

            del user_sockets[username]
            del clients[client]

            for room in rooms.values():

                if client in room:
                    room.remove(client)

        client.close()


def handle_client(client):

    while True:

        try:

            data = recv_json(client)

            if not data:
                break

            msg_type = data.get("type")

            if msg_type == "join":

                username = data["username"]
                room = data["room"]

                with lock:

                    clients[client] = username
                    user_sockets[username] = client

                    if room not in rooms:
                        rooms[room] = []

                    rooms[room].append(client)

                send_json(client, {
                    "type": "info",
                    "message": f"Joined room {room}"
                })

                broadcast_room(room, {
                    "type": "info",
                    "message": f"{username} joined the room"
                }, exclude=client)

            elif msg_type == "message":

                room = data["room"]
                username = clients.get(client)

                broadcast_room(room, {
                    "type": "message",
                    "sender": username,
                    "content": data["content"]
                })

            elif msg_type == "private":

                to_user = data["to"]
                username = clients.get(client)

                if to_user in user_sockets:

                    send_json(user_sockets[to_user], {
                        "type": "private",
                        "from": username,
                        "content": data["content"]
                    })

            elif msg_type == "secret":

                to_user = data["to"]

                if to_user in user_sockets:

                    send_json(user_sockets[to_user], {
                        "type": "secret",
                        "from": clients[client],
                        "content": data["content"]
                    })

        except:
            break

    remove_client(client)


def start_server():

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

        threading.Thread(target=handle_client, args=(secure_client,)).start()


if __name__ == "__main__":
    start_server()