import socket
import threading
from protocol import send_json, recv_json

HOST="127.0.0.1"
PORT=5000

def receive(sock):
    while True:
        data=recv_json(sock)

        if not data:
            break

        if data["type"]=="message":
            print(f"[{data['sender']}]: {data['content']}")

        elif data["type"]=="private":
            print(f"[PRIVATE from {data['from']}]: {data['content']}")

        elif data["type"]=="info":
            print("[INFO]",data["message"])

def start_client():

    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((HOST,PORT))

    threading.Thread(target=receive,args=(sock,),daemon=True).start()

    username=input("Enter username: ")
    room=input("Enter room: ")

    send_json(sock,{
        "type":"join",
        "username":username,
        "room":room
    })

    while True:

        msg=input()

        if msg.startswith("/private"):
            _,to_user,content=msg.split(" ",2)

            send_json(sock,{
                "type":"private",
                "to":to_user,
                "content":content
            })

        else:
            send_json(sock,{
                "type":"message",
                "room":room,
                "content":msg
            })

if __name__=="__main__":
    start_client()