import socket
import ssl
import threading
import time
from protocol import send_json

HOST = "127.0.0.1"   # change if server is on another machine
PORT = 5000

NUM_CLIENTS = 20     # try 5, 10, 20, 50

connected_clients = []
success_count = 0
connection_times = []
lock = threading.Lock()


def simulate_client(client_id):
    global success_count

    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        secure_sock = context.wrap_socket(sock)

        # Measure connection start time
        connect_start = time.time()

        secure_sock.connect((HOST, PORT))

        # Measure connection end time
        connect_end = time.time()

        connection_latency = connect_end - connect_start

        username = f"user_{client_id}"

        send_json(secure_sock, {
            "type": "join",
            "username": username,
            "room": "loadtest"
        })

        time.sleep(0.2)

        message_start = time.time()

        send_json(secure_sock, {
            "type": "message",
            "room": "loadtest",
            "content": f"Latency test from {username}"
        })

        message_end = time.time()

        message_latency = message_end - message_start

        with lock:
            success_count += 1
            connection_times.append(connection_latency)

        print(f"[Client {client_id}] Connected in {connection_latency:.4f} seconds | "
              f"Message sent in {message_latency:.4f} seconds")

        connected_clients.append(secure_sock)

    except Exception as e:
        print(f"[ERROR] Client {client_id} failed:", e)


def main():
    print(f"\nStarting scalability + latency test with {NUM_CLIENTS} clients...\n")

    test_start_time = time.time()

    threads = []

    for i in range(NUM_CLIENTS):
        t = threading.Thread(target=simulate_client, args=(i,))
        t.start()
        threads.append(t)
        time.sleep(0.05)  # Prevent burst overload

    for t in threads:
        t.join()

    test_end_time = time.time()

    total_duration = test_end_time - test_start_time

    print("\n------ TEST RESULT ------")

    print("Clients requested:", NUM_CLIENTS)
    print("Clients connected:", success_count)

    success_rate = (success_count / NUM_CLIENTS) * 100
    print("Connection success rate:", round(success_rate, 2), "%")

    print("Total test duration:", round(total_duration, 3), "seconds")

    if connection_times:
        avg_connection_latency = sum(connection_times) / len(connection_times)
        print("Average connection latency:",
              round(avg_connection_latency, 4), "seconds")

        max_latency = max(connection_times)
        print("Max connection latency:",
              round(max_latency, 4), "seconds")

        min_latency = min(connection_times)
        print("Min connection latency:",
              round(min_latency, 4), "seconds")

    if success_count == NUM_CLIENTS:
        print("Server handled full load successfully.")
    else:
        print("Some connections failed under load.")

    print("\nPerformance evaluation completed.\n")


if __name__ == "__main__":
    main()