import Constants
import helpers


robotDirection = 0
robotCoords = []


def extractCoordinates(string):
    coordinates = []
    for item in string.split():
        try:
            coordinates.append(int(item))
        except ValueError:
            pass
    return coordinates


class robotController:

    def __init__(self, sock):
        self.r_direction = None
        self.r_coords = None
        self.r_previousCoords = None
        self.r_sock = sock

    def findDirection(self):

        if self.r_coords[0] - self.r_previousCoords[0] == 1:
            self.r_direction = 1  # right
        elif self.r_coords[0] - self.r_previousCoords[0] == -1:
            self.r_direction = 2  # left
        elif self.r_coords[1] - self.r_previousCoords[1] == 1:
            self.r_direction = 3  # up
        elif  self.r_coords[1] - self.r_previousCoords[1] == -1:
            self.r_direction = 4  # down
        # elif  self.r_coords == self.r_previousCoords : # Obstacle encountered in first move
        #     self.tryEveryDirection()
        else :
            print("Something went wrong while trying to find direction")

        return self.r_direction

    # def tryEveryDirection(self):
    #
    #     self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
    #     self.r_sock.sendall(Constants.SERVER_MOVE.encode())
    #     received_data = helpers.receiveClientMessage(self.r_sock)
    #     coords1 = extractCoordinates(received_data)
    #     self.r_previousCoords = self.r_coords
    #     self.r_coords = coords1
    #     self.findDirection()

    def findCurrentdirectionPosition(self):
        self.r_sock.sendall(Constants.SERVER_MOVE.encode())
        received_data = helpers.receiveClientMessage(self.r_sock)
        self.r_coords = extractCoordinates(received_data)

        self.r_sock.sendall(Constants.SERVER_MOVE.encode())
        received_data = helpers.receiveClientMessage(self.r_sock)
        self.r_previousCoords = self.r_coords
        self.r_coords = extractCoordinates(received_data)

        self.r_direction = self.findDirection()

    def guideToTarget(self):

        '''
                if the robot is to the left of the origin,
                ie. x coordinate is negative, move towards
                right until I reach (0,y).
        '''

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

    def changeDirectionRight(self):
        if self.r_direction == 1:
            return

        if self.r_direction == 2:
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = helpers.receiveClientMessage(self.r_sock)
            # check if we have received ok
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = helpers.receiveClientMessage(self.r_sock)
            # check if we have received ok
            self.r_direction = 1
            return

        if self.r_direction == 3:
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = helpers.receiveClientMessage(self.r_sock)
            # check if we have received ok
            self.r_direction = 1
            return

        if self.r_direction == 4:
            self.r_sock.sendall(Constants.SERVER_TURN_LEFT.encode())
            received_data = helpers.receiveClientMessage(self.r_sock)
            # check if we have received ok
            self.r_direction = 1
            return

    def changeDirectionLeft(self):
        if self.r_direction == 1:
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = helpers.receiveClientMessage(self.r_sock)
            # check if we have received ok
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = helpers.receiveClientMessage(self.r_sock)
            # check if we have received ok
            self.r_direction = 2
            return

        if self.r_direction == 2:
            return

        if self.r_direction == 3:
            self.r_sock.sendall(Constants.SERVER_TURN_LEFT.encode())
            received_data = helpers.receiveClientMessage(self.r_sock)
            # check if we have received ok
            self.r_direction = 2

        if self.r_direction == 4:
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = helpers.receiveClientMessage(self.r_sock)
            # check if we have received ok
            self.r_direction = 2

    def changeDirectionUp(self):
        if self.r_direction == 1:
            self.r_sock.sendall(Constants.SERVER_TURN_LEFT.encode())
            received_data = helpers.receiveClientMessage(self.r_sock)
            # check if we have received ok
            self.r_direction = 3
            return

        if self.r_direction == 2:
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = helpers.receiveClientMessage(self.r_sock)
            # check if we have received ok
            self.r_direction = 3
            return

        if self.r_direction == 3:
            return

        if self.r_direction == 4:
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = helpers.receiveClientMessage(self.r_sock)
            # check if we have received ok
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = helpers.receiveClientMessage(self.r_sock)
            # check if we have received ok
            self.r_direction = 3
            return

    def changeDirectionDown(self):
        if self.r_direction == 1:
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = helpers.receiveClientMessage(self.r_sock)
            # check if we have received ok
            self.r_direction = 4
            return

        if self.r_direction == 2:
            self.r_sock.sendall(Constants.SERVER_TURN_LEFT.encode())
            received_data = helpers.receiveClientMessage(self.r_sock)
            # check if we have received ok
            self.r_direction = 4
            return

        if self.r_direction == 3:
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = helpers.receiveClientMessage(self.r_sock)
            # check if we have received ok
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = helpers.receiveClientMessage(self.r_sock)
            # check if we have received ok
            self.r_direction = 4
            return

        if self.r_direction == 4:
            return

    def detectObstacle(self):
        if self.r_coords == self.r_previousCoords:
            return True

    def traverseObstacle(self):
        if self.r_direction == 1 :

            self.changeDirectionUp()
            self.move()
            self.changeDirectionRight()
            self.move()
            self.move()
            self.changeDirectionDown()
            self.move()
            self.changeDirectionRight()

        elif self.r_direction == 2 :

            self.changeDirectionUp()
            self.move()
            self.changeDirectionLeft()
            self.move()
            self.move()
            self.changeDirectionDown()
            self.move()
            self.changeDirectionLeft()

        elif self.r_direction == 3 :

            self.changeDirectionLeft()
            self.move()
            self.changeDirectionUp()
            self.move()
            self.move()
            self.changeDirectionRight()
            self.move()
            self.changeDirectionUp()

        else :
            self.changeDirectionLeft()
            self.move()
            self.changeDirectionDown()
            self.move()
            self.move()
            self.changeDirectionRight()
            self.move()
            self.changeDirectionDown()


    def checkIfReachedDestination(self):
        if self.r_coords == [0, 0]:
            self.r_sock.sendall(Constants.SERVER_PICK_UP.encode())
            received_data = helpers.receiveClientMessage(self.r_sock)

            self.r_sock.sendall(Constants.SERVER_LOGOUT.encode())
            self.r_sock.close()
            return True

    def move(self):
        self.r_sock.sendall(Constants.SERVER_MOVE.encode())
        received_data = helpers.receiveClientMessage(self.r_sock)
        coords1 = extractCoordinates(received_data)
        self.r_previousCoords = self.r_coords
        self.r_coords = coords1
        if self.detectObstacle():
            self.traverseObstacle()
        self.checkIfReachedDestination()

