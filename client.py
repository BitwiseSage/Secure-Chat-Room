import socket
import threading
import os
from protocol import send_json, recv_json

HOST="127.0.0.1"
PORT=5000

def receive(sock):

    while True:

        data=recv_json(sock)

        if not data:
            break

        msg_type=data.get("type")

        if msg_type=="message":
            print(f"[{data['sender']}]: {data['content']}")

        elif msg_type=="private":
            print(f"[PRIVATE from {data['from']}]: {data['content']}")

        elif msg_type=="info":
            print("[INFO]",data["message"])

        elif msg_type=="file":

            filename="received_files/"+data["filename"]
            filesize=data["filesize"]

            remaining=filesize

            with open(filename,"wb") as f:

                while remaining>0:

                    chunk=sock.recv(min(4096,remaining))

                    f.write(chunk)

                    remaining-=len(chunk)

            print("[FILE RECEIVED]",filename)

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

        elif msg.startswith("/file"):

            _,filepath=msg.split(" ",1)

            filesize=os.path.getsize(filepath)
            filename=os.path.basename(filepath)

            send_json(sock,{
                "type":"file",
                "filename":filename,
                "filesize":filesize,
                "room":room
            })

            with open(filepath,"rb") as f:

                while chunk:=f.read(4096):
                    sock.sendall(chunk)

        else:

            send_json(sock,{
                "type":"message",
                "room":room,
                "content":msg
            })

if __name__=="__main__":
    start_client()