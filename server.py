import socket
import threading
import ssl
from protocol import send_json, recv_json

HOST="0.0.0.0"
PORT=5000

clients={}
rooms={}
lock=threading.Lock()

def handle_client(client):

    while True:

        try:

            data=recv_json(client)

            if not data:
                break

            if data["type"]=="message":

                print("Message received")

        except:
            break

    client.close()

def start_server():

    context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem",keyfile="key.pem")

    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    server.bind((HOST,PORT))
    server.listen()

    print("Server running with SSL")

    while True:

        client,addr=server.accept()

        secure_client=context.wrap_socket(client,server_side=True)

        threading.Thread(target=handle_client,args=(secure_client,)).start()

if __name__=="__main__":
    start_server()