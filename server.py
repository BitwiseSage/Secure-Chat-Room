import socket
from encryption_utils import encrypt_message, decrypt_message
import threading
import ssl
import os
from protocol import send_json, recv_json
from encryption_utils import generate_key

HOST = "0.0.0.0"
PORT = 5000

clients = {}       # dictionary that maps socket -> username
user_sockets = {}  # username -> socket (useful for private messages)
rooms = {}         # room -> list of sockets (tracks which client belongs to which room)
lock = threading.Lock() #used because multiple users are allowed

def broadcast_room(room, message, exclude=None):  #sending message to everyone in the room
    if room in rooms:
        for client in rooms[room]:
            if client != exclude:
                try:
                    send_json(client, message)       #sends message in JSON format
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

        client.close()			#close socket connection

def handle_client(client):		#each connected client is handeled in a different thread
    while True:
        try:
            data = recv_json(client)
            if not data:
                break

            msg_type = data.get("type")			#join , message , secret , file.....
            print("Received type:", msg_type)

            if msg_type == "join":			#adding user to room
                username = data["username"]
                room = data["room"]

                with lock:
                    clients[client] = username
                    user_sockets[username] = client

                    if room not in rooms:
                        rooms[room] = []
                    rooms[room].append(client)

                send_json(client, {"type": "info", "message": f"Joined room {room}"})
                broadcast_room(room, {"type": "info", "message": f"{username} joined the room"}, exclude=client)

            elif msg_type == "message":			#message sent in the room
                room = data["room"]
                username = clients.get(client)
                broadcast_room(room, {
                    "type": "message",
                    "sender": username,
                    "content": data["content"]
                })

            elif msg_type == "private":			#private message sent
                to_user = data["to"]
                username = clients.get(client)
                if to_user in user_sockets:
                    send_json(user_sockets[to_user], {
                        "type": "private",
                        "from": username,
                        "content": data["content"]
                    })

            elif msg_type == "file":		#sharing files (yet to be worked on)
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
                    remaining -= len(chunk)
                    for member in rooms[room]:
                        if member != client:
                            member.sendall(chunk)
            
            elif msg_type == "secret":			#sends encryptes message
                to_user = data["to"]
                if to_user in user_sockets:
                    send_json(user_sockets[to_user], {
                        "type": "secret",
                        "from": clients[client],
                        "content": data["content"]   # just forward
                    })
        except:
            break

    remove_client(client)

def start_server():
    key = generate_key()			#using fernet cryptography library
    
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)			#creates SSL context
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")	#LOADING SSL CERTIFICATE AND PRIVATE KEY

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		#start TCP server (creating socket)
    server.bind((HOST, PORT))						#binding adress of host and port
    server.listen(5)							#start listening for clients

    print("Server running with SSL...")

    while True:
        client, addr = server.accept()					#accept client connections
        secure_client = context.wrap_socket(client, server_side=True)	#wrap socket with SSL encryption
        print(f"Connection from {addr}")
        threading.Thread(target=handle_client, args=(secure_client,)).start()	#multithreading , creates new thread for each client

if __name__ == "__main__":				#server startes when file is executing
    start_server()
