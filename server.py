import socket
import threading


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    connected = True
    while connected:
        try:
            msg = conn.recv(1024)
            print(msg)
            if msg:
                broadcast(msg, conn)
        except:
            connected = False

    print(f"[DISCONNECTED] {addr} disconnected.")
    conn.close()


def broadcast(msg, sender):
    for client in clients:
        if client != sender:
            client.send(msg)


def start_server():
    print("[STARTING] server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 9999))
    server.listen()

    print(f"[LISTENING] server is listening on localhost:5555")

    while True:
        conn, addr = server.accept()
        clients.append(conn)

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


clients = []

start_server()