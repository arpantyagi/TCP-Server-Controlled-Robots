# Created by Arpan Tyagi
# for course BIE-PSI
# at FIT CVUT
import logging
import socket

from RobotConnectionHandler import *

HOST = '127.0.0.1'
PORT = 54321


def run_server(HOST, PORT):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()
    while True:

        try:
            client_sock, addr = sock.accept()
            logging.debug('Connection from {}'.format(addr))
            robot = RobotConnectionHandler(client_sock)

            if robot.authenticateConnection():
                if robot.findCurrentPosition():
                    robot.guideToTarget()

        except socket.timeout:
            logging.debug("Socket Timed-Out, Closing Conection")
            client_sock.close()
        except KeyboardInterrupt:
            logging.debug("Server Stopped by User")




if __name__ == '__main__':
    run_server(HOST, PORT)