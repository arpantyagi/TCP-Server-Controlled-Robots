import socket
import robotAuthentication as auth
import moveRobot as mv
import helpers
HOST = '127.0.0.1'
PORT = 54322

def run_server(HOST, PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()
    while True:
        client_sock, addr = sock.accept()
        print('Connection from', addr)
        auth.robotAuthentication(client_sock)
        mv.findCurrentdirectionPosition(client_sock)

if __name__ == '__main__':
    run_server(HOST, PORT)