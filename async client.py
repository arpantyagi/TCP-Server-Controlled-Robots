import socket
import threading


HOST = '127.0.0.1'
PORT = 54321

BUFFSIZE = 4096


def run_server(HOST, PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()

    while True:
        clientSock, addr = sock.accept()
        print('Connection from', addr)
        thread = threading.Thread(target=handle_client, args=[client_sock])
        thread.start()


def handle_client(sock):
    while True:
        received_data = sock.recv(BUFFSIZE)
        if not received_data:
            break
        sock.sendall(received_data)

    print("Client disconnected:", sock.getpeername())
    sock.close()

if __name__ == '__main__':
    run_server()


