import logging
import socket
import time
from time import sleep

from constants import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(message)s')


class RobotConnectionHandler:

    def __init__(self, sock):
        self.r_sock = sock
        self.r_username = None
        self.r_hash = None
        self.r_clientHash = None
        self.r_key = None
        self.r_coords = None
        self.r_previousCoords = None
        self.r_direction = None
        self.r_pipe = str()
        self.reachedDestination = False

    def closeConnection(self):
        logging.debug('Closing Connection with Client: {}'.format(self.r_sock.getpeername()))
        self.r_sock.close()
        raise RuntimeError()

    def calculateHash(self, client=False):
        hashSum: int = 0
        for char in self.r_username:
            hashSum = hashSum + ord(char)
        if client:
            return ((hashSum * 1000) % 65536 + AUTHENTICATIONKEYS[self.r_key][1]) % MOD16
        return ((hashSum * 1000) % 65536 + AUTHENTICATIONKEYS[self.r_key][0]) % MOD16

    def receiveMessage(self, maxMessageLength=12, timeout=1):

        messageEndIndex = self.r_pipe.find('\a\b')
        if messageEndIndex == -1:
            while True:
                if len(self.r_pipe) > maxMessageLength:
                    self.sendMessage(SERVER_SYNTAX_ERROR)
                    self.closeConnection()
                    raise RuntimeError()
                self.r_sock.settimeout(timeout)
                received_data = self.r_sock.recv(1024).decode()
                self.r_pipe += received_data

                messageEndIndex = self.r_pipe.find('\a\b')
                if messageEndIndex == -1:
                    continue
                else:
                    nextMessage = self.r_pipe[:messageEndIndex]
                    self.r_pipe = self.r_pipe[messageEndIndex + 2:]
                    logging.debug("Received message: {}".format(nextMessage))
                    if nextMessage == "RECHARGING":
                        t_end = time.time() + TIMEOUT_RECHARGING
                        while time.time() < t_end:
                            try:
                                self.r_sock.settimeout(5)
                                status = self.receiveMessage(timeout=5)
                                if status != 'FULL POWER' and status != '':
                                    self.sendMessage(SERVER_LOGIC_ERROR)
                                    self.closeConnection()
                                    raise RuntimeError()
                                else:
                                    break
                            except socket.timeout as e:
                                logging.debug("Socket Timed out while waiting for robot to charge")
                                self.closeConnection()
                                raise RuntimeError()

                    else:
                        return nextMessage
        else:
            nextMessage = self.r_pipe[:messageEndIndex]
            self.r_pipe = self.r_pipe[messageEndIndex + 2:]
            return nextMessage

    def sendMessage(self, message: str):

        try:
            self.r_sock.sendall(message.encode())
            logging.debug('Sent message: {}'.format(message))

        except BrokenPipeError:
            logging.debug("Packet could not be sent, Connection has been closed")

    def authenticateConnection(self):
        """
        Receives a username, validates it.
        Send request to send key, validates the key

        :return: None
        """
        self.r_username = self.receiveMessage(USERNAME_MAX_LEN)
        if len(self.r_username) > USERNAME_MAX_LEN:
            self.sendMessage(SERVER_SYNTAX_ERROR)
            self.closeConnection()
            return False

        # Request Key
        self.sendMessage(SERVER_KEY_REQUEST)

        # Receive Keys
        try:
            self.r_key = int(self.receiveMessage())
        except ValueError as e:
            logging.debug(e)
            self.sendMessage(SERVER_SYNTAX_ERROR)
            self.closeConnection()
            logging.debug("Invalid Key format")
            return False

        # Validate Key
        if type(self.r_key) != int:
            self.sendMessage(SERVER_SYNTAX_ERROR)
            self.closeConnection()
            return False
        if self.r_key > 4 or self.r_key < 0:
            self.sendMessage(SERVER_KEY_OUT_OF_RANGE_ERROR)
            self.closeConnection()
            return False

        # Calculate and Send Hash
        self.r_hash = self.calculateHash()
        self.sendMessage(f"{self.r_hash}\a\b")

        # Receive client hash and verify
        self.r_clientHash = self.receiveMessage(CONFIRMATION_MAX_LEN)
        if not self.r_clientHash.isnumeric():
            self.sendMessage(SERVER_SYNTAX_ERROR)
            self.closeConnection()
            return False

        self.r_clientHash = int(self.r_clientHash)
        if self.r_clientHash > 65536:
            self.sendMessage(SERVER_SYNTAX_ERROR)
            self.closeConnection()
            return False

        if self.r_clientHash != self.calculateHash(client=True):
            self.sendMessage(SERVER_LOGIN_FAILED)
            self.closeConnection()
            logging.debug("Authentication Failed!")
            return False

        else:
            self.sendMessage(SERVER_OK)
            logging.debug("Authentication Complete!")
            return True

    def extractCoordinates(self, received_data):
        coordinatesF = list()
        coordinates = received_data.split()[1:]
        if received_data[-1:] == " ":
            self.sendMessage(SERVER_SYNTAX_ERROR)
            self.closeConnection()
            raise RuntimeError
        for item in coordinates:
            try:
                coordinatesF.append(int(item))
            except ValueError as e:
                logging.info(e)
                self.sendMessage(SERVER_SYNTAX_ERROR)
                self.closeConnection()
                raise RuntimeError
        self.r_previousCoords = self.r_coords
        self.r_coords = coordinatesF

    def tryEveryDirection(self):

        logging.debug("Encountered Obstacle without knowing direction")
        self.sendMessage(SERVER_TURN_RIGHT)
        self.receiveMessage()
        self.findCurrentPosition()

    def findDirection(self):
        if self.r_coords[0] - self.r_previousCoords[0] == 1:
            self.r_direction = WEST
        elif self.r_coords[0] - self.r_previousCoords[0] == -1:
            self.r_direction = EAST
        elif self.r_coords[1] - self.r_previousCoords[1] == 1:
            self.r_direction = NORTH
        elif self.r_coords[1] - self.r_previousCoords[1] == -1:
            self.r_direction = SOUTH
        # Obstacle encountered in first move
        elif self.r_coords == self.r_previousCoords:
            self.tryEveryDirection()
        else:
            logging.debug("Something went wrong while trying to find direction")
            self.closeConnection()
        logging.debug(self.r_direction)

    def findCurrentPosition(self):
        self.sendMessage(SERVER_TURN_LEFT)
        received_data = self.receiveMessage()
        self.extractCoordinates(received_data)
        self.move()
        self.findDirection()
        return True
    
    def move(self):
        self.sendMessage(SERVER_MOVE)
        received_data = self.receiveMessage()
        self.extractCoordinates(received_data)
        logging.debug(self.r_direction)
        if self.detectObstacle():
            self.traverseObstacle()
        self.checkIfReachedDestination()
        
    def checkIfReachedDestination(self):
        if self.r_coords == [0, 0]:
            logging.debug("Reached Origin")
            self.sendMessage(SERVER_PICK_UP)
            self.reachedDestination = True
            self.receiveMessage(CLIENT_MESSAGE_MAX_LEN)
            self.sendMessage(SERVER_LOGOUT)
            self.closeConnection()
            return True

    def changeDirectionRight(self):
        logging.debug("Changing Direction to East")
        if self.r_direction == 1:
            return

        if self.r_direction == 2:
            self.sendMessage(SERVER_TURN_RIGHT)
            self.receiveMessage()
            # check if we have received ok
            self.sendMessage(SERVER_TURN_RIGHT)
            self.receiveMessage()
            # check if we have received ok
            self.r_direction = 1
            return

        if self.r_direction == 3:
            self.sendMessage(SERVER_TURN_RIGHT)
            self.receiveMessage()
            # check if we have received ok
            self.r_direction = 1
            return

        if self.r_direction == 4:
            self.sendMessage(SERVER_TURN_LEFT)
            self.receiveMessage()
            # check if we have received ok
            self.r_direction = 1
            return

    def changeDirectionLeft(self):
        logging.debug("Changing Direction to West")
        if self.r_direction == 1:
            self.sendMessage(SERVER_TURN_RIGHT)
            self.receiveMessage()
            # check if we have received ok
            self.sendMessage(SERVER_TURN_RIGHT)
            self.receiveMessage()
            # check if we have received ok
            self.r_direction = 2
            return

        if self.r_direction == 2:
            return

        if self.r_direction == 3:
            self.sendMessage(SERVER_TURN_LEFT)
            self.receiveMessage()
            # check if we have received ok
            self.r_direction = 2

        if self.r_direction == 4:
            self.sendMessage(SERVER_TURN_RIGHT)
            self.receiveMessage()
            # check if we have received ok
            self.r_direction = 2

    def changeDirectionUp(self):
        logging.debug("Changing Direction to North")
        if self.r_direction == 1:
            self.sendMessage(SERVER_TURN_LEFT)
            self.receiveMessage()
            # check if we have received ok
            self.r_direction = 3
            return

        if self.r_direction == 2:
            self.sendMessage(SERVER_TURN_RIGHT)
            self.receiveMessage()
            # check if we have received ok
            self.r_direction = 3
            return

        if self.r_direction == 3:
            return

        if self.r_direction == 4:
            self.sendMessage(SERVER_TURN_RIGHT)
            self.receiveMessage()
            # check if we have received ok
            self.sendMessage(SERVER_TURN_RIGHT)
            self.receiveMessage()
            # check if we have received ok
            self.r_direction = 3
            return

    def changeDirectionDown(self):
        logging.debug("Changing Direction to South")
        if self.r_direction == 1:
            self.sendMessage(SERVER_TURN_RIGHT)
            self.receiveMessage()
            # check if we have received ok
            self.r_direction = 4
            return

        if self.r_direction == 2:
            self.sendMessage(SERVER_TURN_LEFT)
            self.receiveMessage()
            # check if we have received ok
            self.r_direction = 4
            return

        if self.r_direction == 3:
            self.sendMessage(SERVER_TURN_RIGHT)
            self.receiveMessage()
            # check if we have received ok
            self.sendMessage(SERVER_TURN_RIGHT)
            self.receiveMessage()
            # check if we have received ok
            self.r_direction = 4
            return

        if self.r_direction == 4:
            return

    def detectObstacle(self):
        if self.r_coords == self.r_previousCoords:
            logging.debug("Obstacle Detected")
            return True

    def traverseObstacle(self):
        if self.r_direction == WEST:

            self.changeDirectionUp()
            self.move()
            self.changeDirectionRight()
            self.move()
            self.move()
            self.changeDirectionDown()
            self.move()
            self.changeDirectionRight()
            logging.debug("Obstacle Traversed")
        elif self.r_direction == EAST:

            self.changeDirectionUp()
            self.move()
            self.changeDirectionLeft()
            self.move()
            self.move()
            self.changeDirectionDown()
            self.move()
            self.changeDirectionLeft()
            logging.debug("Obstacle Traversed")

        elif self.r_direction == NORTH:

            self.changeDirectionLeft()
            self.move()
            self.changeDirectionUp()
            self.move()
            self.move()
            self.changeDirectionRight()
            self.move()
            self.changeDirectionUp()
            logging.debug("Obstacle Traversed")

        elif self.r_direction == SOUTH:
            self.changeDirectionLeft()
            self.move()
            self.changeDirectionDown()
            self.move()
            self.move()
            self.changeDirectionRight()
            self.move()
            self.changeDirectionDown()
            logging.debug("Obstacle Traversed")

        else:
            self.findCurrentPosition()

    def guideToTarget(self):

        while self.r_coords != [0, 0]:

            if self.r_coords[0] < 0:
                self.changeDirectionRight()
                self.move()

            if self.r_coords[1] < 0:
                self.changeDirectionUp()
                self.move()

            if self.r_coords[0] > 0:
                self.changeDirectionLeft()
                self.move()

            if self.r_coords[1] > 0:
                self.changeDirectionDown()
                self.move()
