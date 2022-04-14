
import constants


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
        print('Client disconnected:', self.r_sock.getpeername())
        self.r_sock.close()

    def calculateHash(self, client=False):
        hashSum = 0
        for char in self.r_username:
            hashSum = hashSum + ord(char)

        if (client):
            return ((hashSum * 1000) % 65536 + constants.AUTHENTICATIONKEYS[self.r_key][1]) % 65536
        return ((hashSum * 1000) % 65536 + constants.AUTHENTICATIONKEYS[self.r_key][0]) % 65536

    def receiveMessage(self):
        while True:
            self.r_sock.settimeout(1)
            received_data = self.r_sock.recv(18).decode()
            self.r_pipe += received_data

            messageEndIndex = self.r_pipe.find('\a\b')
            if messageEndIndex == -1:
                pass
            else:
                nextMessage = self.r_pipe[:messageEndIndex]
                self.r_pipe = self.r_pipe[messageEndIndex + 2:]
                print(nextMessage)
                return nextMessage

    def sendMessage(self, message: str):
        print('Sending Message: ' + message)
        self.r_sock.sendall(message.encode())

    def authenticateConnection(self):

        # Receive Username
        self.r_username = self.receiveMessage()
        if self.r_username is None:
            self.closeConnection()
            print("Something went wrong while getting username")
            return False

        if len(self.r_username) > constants.USERNAME_MAX_LEN:
            self.sendMessage(constants.SERVER_SYNTAX_ERROR)
            self.closeConnection()
            return False

        # Request Key
        self.sendMessage(constants.SERVER_KEY_REQUEST)
        # Receive Keys
        try:
            self.r_key = int(self.receiveMessage())
        except ValueError as e:
            print(e)
            self.sendMessage(constants.SERVER_SYNTAX_ERROR)
            self.closeConnection()
            print("Key is in wrong format")
            return False

        if self.r_key is None:
            self.closeConnection()
            print("Something went wrong while getting KEY")
            return False

        if type(self.r_key) != int:
            self.sendMessage(constants.SERVER_SYNTAX_ERROR)
            self.closeConnection()
            return False
        # Check Key Range
        if (self.r_key > 4 or self.r_key < 0):
            self.sendMessage(constants.SERVER_KEY_OUT_OF_RANGE_ERROR)
            self.closeConnection()
            return False


        # Get Hash
        self.r_hash = self.calculateHash()
        self.sendMessage(f"{(self.r_hash)}\a\b")
        clientHashString = self.receiveMessage()
        if not clientHashString.isnumeric():
            self.sendMessage(constants.SERVER_SYNTAX_ERROR)
            self.closeConnection()
            return False



        self.r_clientHash = int(clientHashString)

        if  self.r_clientHash > 65536:
            self.sendMessage(constants.SERVER_SYNTAX_ERROR)
            self.closeConnection()
            return False

        if self.r_clientHash != self.calculateHash(client=True):
            self.sendMessage(constants.SERVER_LOGIN_FAILED)
            self.closeConnection()
            print("Authentication Failed!")
            return False


        else:
            # self.sendMessage(constants.SERVER_OK)
            self.sendMessage("200 OK\a\b")
            print("Authentication Complete!")
            return True

    def extractCoordinates(self, recived_data):
        coordinates = []
        for item in recived_data.split():
            try:
                coordinates.append(int(item))
            except ValueError as e:
                print(e)
        self.r_previousCoords = self.r_coords
        self.r_coords = coordinates

    def tryEveryDirection(self):

        print("Encountered Obstacle without knowing direction")
        self.sendMessage(constants.SERVER_TURN_RIGHT)
        self.findCurrentPosition()

    def findDirection(self):
        print("trying to find direction")
        if self.r_coords[0] - self.r_previousCoords[0] == 1:
            self.r_direction = 1  # right
        elif self.r_coords[0] - self.r_previousCoords[0] == -1:
            self.r_direction = 2  # left
        elif self.r_coords[1] - self.r_previousCoords[1] == 1:
            self.r_direction = 3  # up
        elif self.r_coords[1] - self.r_previousCoords[1] == -1:
            self.r_direction = 4  # down
        elif  self.r_coords == self.r_previousCoords : # Obstacle encountered in first move
             self.tryEveryDirection()
        else:
            print("Something went wrong while trying to find direction")
            self.closeConnection()

    def findCurrentPosition(self):
        self.sendMessage(constants.SERVER_MOVE)
        received_data = self.receiveMessage()
        self.extractCoordinates(received_data)

        self.sendMessage(constants.SERVER_MOVE)
        received_data = self.receiveMessage()
        self.r_previousCoords = self.r_coords
        self.extractCoordinates(received_data)
        self.findDirection()
        return True
    
    def move(self):
        self.sendMessage(constants.SERVER_MOVE)
        received_data = self.receiveMessage()
        self.extractCoordinates(received_data)

        if self.detectObstacle():
            self.traverseObstacle()
        self.checkIfReachedDestination()
        
    def checkIfReachedDestination(self):
        if self.r_coords == [0, 0]:
            print("Reached Origin")
            self.sendMessage(constants.SERVER_PICK_UP)
            self.reachedDestination = True
            received_data = self.receiveMessage()
            self.sendMessage(constants.SERVER_LOGOUT)
            self.closeConnection()
            return True

    def changeDirectionRight(self):
        print("Changing Direction to East")
        if self.r_direction == 1:
            return

        if self.r_direction == 2:
            self.sendMessage(constants.SERVER_TURN_RIGHT)
            received_data = self.receiveMessage()
            # check if we have received ok
            self.sendMessage(constants.SERVER_TURN_RIGHT)
            received_data = self.receiveMessage()
            # check if we have received ok
            self.r_direction = 1
            return

        if self.r_direction == 3:
            self.sendMessage(constants.SERVER_TURN_RIGHT)
            received_data = self.receiveMessage()
            # check if we have received ok
            self.r_direction = 1
            return

        if self.r_direction == 4:
            self.sendMessage(constants.SERVER_TURN_LEFT)
            received_data = self.receiveMessage()
            # check if we have received ok
            self.r_direction = 1
            return

    def changeDirectionLeft(self):
        print("Changing Direction to West")
        if self.r_direction == 1:
            self.sendMessage(constants.SERVER_TURN_RIGHT)
            received_data = self.receiveMessage()
            # check if we have received ok
            self.sendMessage(constants.SERVER_TURN_RIGHT)
            received_data = self.receiveMessage()
            # check if we have received ok
            self.r_direction = 2
            return

        if self.r_direction == 2:
            return

        if self.r_direction == 3:
            self.sendMessage(constants.SERVER_TURN_LEFT)
            received_data = self.receiveMessage()
            # check if we have received ok
            self.r_direction = 2

        if self.r_direction == 4:
            self.sendMessage(constants.SERVER_TURN_RIGHT)
            received_data = self.receiveMessage()
            # check if we have received ok
            self.r_direction = 2

    def changeDirectionUp(self):
        print("Changing Direction to North")
        if self.r_direction == 1:
            self.sendMessage(constants.SERVER_TURN_LEFT)
            received_data = self.receiveMessage()
            # check if we have received ok
            self.r_direction = 3
            return

        if self.r_direction == 2:
            self.sendMessage(constants.SERVER_TURN_RIGHT)
            received_data = self.receiveMessage()
            # check if we have received ok
            self.r_direction = 3
            return

        if self.r_direction == 3:
            return

        if self.r_direction == 4:
            self.sendMessage(constants.SERVER_TURN_RIGHT)
            received_data = self.receiveMessage()
            # check if we have received ok
            self.sendMessage(constants.SERVER_TURN_RIGHT)
            received_data = self.receiveMessage()
            # check if we have received ok
            self.r_direction = 3
            return

    def changeDirectionDown(self):
        print("Changing Direction to South")
        if self.r_direction == 1:
            self.sendMessage(constants.SERVER_TURN_RIGHT)
            received_data = self.receiveMessage()
            # check if we have received ok
            self.r_direction = 4
            return

        if self.r_direction == 2:
            self.sendMessage(constants.SERVER_TURN_LEFT)
            received_data = self.receiveMessage()
            # check if we have received ok
            self.r_direction = 4
            return

        if self.r_direction == 3:
            self.sendMessage(constants.SERVER_TURN_RIGHT)
            received_data = self.receiveMessage()
            # check if we have received ok
            self.sendMessage(constants.SERVER_TURN_RIGHT)
            received_data = self.receiveMessage()
            # check if we have received ok
            self.r_direction = 4
            return

        if self.r_direction == 4:
            return

    def detectObstacle(self):
        if self.r_coords == self.r_previousCoords:
            print("Obstacle Detected")
            return True

    def traverseObstacle(self):
        if self.r_direction == 1:

            self.changeDirectionUp()
            self.move()
            self.changeDirectionRight()
            self.move()
            self.move()
            self.changeDirectionDown()
            self.move()
            self.changeDirectionRight()

        elif self.r_direction == 2:

            self.changeDirectionUp()
            self.move()
            self.changeDirectionLeft()
            self.move()
            self.move()
            self.changeDirectionDown()
            self.move()
            self.changeDirectionLeft()

        elif self.r_direction == 3:

            self.changeDirectionLeft()
            self.move()
            self.changeDirectionUp()
            self.move()
            self.move()
            self.changeDirectionRight()
            self.move()
            self.changeDirectionUp()

        else:
            self.changeDirectionLeft()
            self.move()
            self.changeDirectionDown()
            self.move()
            self.move()
            self.changeDirectionRight()
            self.move()
            self.changeDirectionDown()

    def guideToTarget(self):

        while not self.reachedDestination:

            if self.r_coords[0] < 0:
                self.changeDirectionRight()
                while self.r_coords[0] != 0:
                    self.move()

            if self.r_coords[0] > 0:
                self.changeDirectionLeft()
                while self.r_coords[0] != 0:
                    self.move()

            if self.r_coords[1] < 0:
                self.changeDirectionUp()
                while self.r_coords[1] != 0:
                    self.move()

            if self.r_coords[1] > 0:
                self.changeDirectionDown()
                while self.r_coords[1] != 0:
                    self.move()
