import socket
import threading
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
                send_json(client, message)

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

                send_json(client, {"type": "info", "message": f"Joined room {room}"})

            elif msg_type == "message":
                room = data["room"]
                username = clients.get(client)

                broadcast_room(room,{
                    "type":"message",
                    "sender":username,
                    "content":data["content"]
                })

            elif msg_type == "private":
                to_user = data["to"]
                username = clients.get(client)

                if to_user in user_sockets:
                    send_json(user_sockets[to_user],{
                        "type":"private",
                        "from":username,
                        "content":data["content"]
                    })

        except:
            break

    client.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print("Server running on port",PORT)

    while True:
        client, addr = server.accept()
        print("Connection from",addr)

        threading.Thread(target=handle_client,args=(client,)).start()

if __name__ == "__main__":
    start_server()