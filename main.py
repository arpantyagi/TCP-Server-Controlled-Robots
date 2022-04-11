# Created by Arpan Tyagi
# for course BIE-PSI
# at FIT CVUT

import socket
import robotAuthentication as auth
import helpers
import moveRobot

HOST = '127.0.0.1'
PORT = 54321

def run_server(HOST, PORT):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()

    while True:

        client_sock, addr = sock.accept()
        print('Connection from', addr)

        if not auth.robotAuthentication(client_sock) :
            helpers.closeConnection(client_sock)
        else :
            robo = moveRobot.robotController(client_sock)
            robo.findCurrentdirectionPosition()
            robo.guideToTarget()

if __name__ == '__main__':
    run_server(HOST, PORT)