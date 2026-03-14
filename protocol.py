import json

def send_json(sock, data):
    message = json.dumps(data).encode()
    sock.sendall(message)

def recv_json(sock):
    data = sock.recv(4096)
    if not data:
        return None
    return json.loads(data.decode())