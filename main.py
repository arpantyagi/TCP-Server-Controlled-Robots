# Created by Arpan Tyagi
# for course BIE-PSI
# at FIT CVUT

import socket

from RobotConnectionHandler import RobotConnectionHandler

HOST = '127.0.0.1'
PORT = 54321

def run_server(HOST, PORT):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()

    while True:

        client_sock, addr = sock.accept()
        print('Connection from', addr)
        #client_sock.settimeout(1)
        robot = RobotConnectionHandler(client_sock)

        if robot.authenticateConnection():
            if robot.findCurrentPosition():
                robot.guideToTarget()


if __name__ == '__main__':
    run_server(HOST, PORT)