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

        try:
            client_sock, addr = sock.accept()
            client_sock.settimeout(1)
            print('Connection from', addr)
            robot = RobotConnectionHandler(client_sock)

            if robot.authenticateConnection():
                if robot.findCurrentPosition():
                    robot.guideToTarget()

        except socket.timeout:
            print("Socket Timed-Out, Closing Conection")
            client_sock.close()




if __name__ == '__main__':
    run_server(HOST, PORT)