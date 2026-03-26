import socket
import ssl
import threading
import time
from protocol import send_json

HOST = "127.0.0.1"   # change if server is on another machine
PORT = 5000

NUM_CLIENTS = 20     # change this: try 5, 10, 20, 50

connected_clients = []
success_count = 0
lock = threading.Lock()


def simulate_client(client_id):
    global success_count

    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        secure_sock = context.wrap_socket(sock)

        secure_sock.connect((HOST, PORT))

        username = f"user_{client_id}"

        send_json(secure_sock, {
        "type": "join",
        "username": username,
        "room": "loadtest"
        })

        time.sleep(0.2)

        send_json(secure_sock, {
        "type": "message",
        "room": "loadtest",
        "content": f"Hello from {username}"
        })

        with lock:
            success_count += 1

        connected_clients.append(secure_sock)

    except Exception as e:
        print(f"[ERROR] Client {client_id} failed:", e)


def main():
    print(f"\nStarting scalability test with {NUM_CLIENTS} clients...\n")

    start_time = time.time()

    threads = []

    for i in range(NUM_CLIENTS):
        t = threading.Thread(target=simulate_client, args=(i,))
        t.start()
        threads.append(t)
        time.sleep(0.05)

    for t in threads:
        t.join()

    end_time = time.time()

    print("------ TEST RESULT ------")
    print("Clients requested:", NUM_CLIENTS)
    print("Clients connected:", success_count)
    print("Connection success rate:", (success_count / NUM_CLIENTS) * 100, "%")
    print("Total connection time:", round(end_time - start_time, 3), "seconds")

    print("\nServer scalability test completed.\n")


if __name__ == "__main__":
    main()