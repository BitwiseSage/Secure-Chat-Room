import json

BUFFER_SIZE = 4096

def send_json(sock, data):
    message = json.dumps(data) + "\n"
    sock.sendall(message.encode())

def recv_json(sock):
    buffer = ""
    while True:
        chunk = sock.recv(BUFFER_SIZE).decode()
        if not chunk:
            return None
        buffer += chunk
        if "\n" in buffer:
            message, buffer = buffer.split("\n", 1)
            return json.loads(message)
