# Created by Arpan Tyagi
# for course BIE-PSI
# at FIT CVUT
import socket

from RobotConnectionHandler import *

HOST = '127.0.0.1'
PORT = 54321


def run_server(host, port):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen()
    while True:

        try:
            client_sock, address = sock.accept()
            logging.debug('Connection from {}'.format(address))
            robot = RobotConnectionHandler(client_sock)

            if robot.authenticateConnection():
                if robot.findCurrentPosition():
                    robot.guideToTarget()

        except socket.timeout:
            client_sock.close()
            logging.debug("Socket Timed-Out, Closing Connection")
        except KeyboardInterrupt:
            logging.debug("Server Stopped by User")
        except RuntimeError:
            logging.debug("Socket was closed due to Logic Error, Now accepting new connections.")


if __name__ == '__main__':
    run_server(HOST, PORT)
