import socket
import threading

HOST = "0.0.0.0"
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("Server started on port", PORT)

while True:
    client, addr = server.accept()
    print("Client connected:", addr)

def handle_client(client):
    print("Handling new client")