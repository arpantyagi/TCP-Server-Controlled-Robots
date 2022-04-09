import Constants
import re

robotDirection = 0
robotCoords = []


def extractCoordinates(self, string):
    return re.findall(r'\d+', string)


class robotController:

    def __init__(self, sock):
        self.r_direction = None
        self.r_coords = None
        self.r_previousCoords = None
        self.r_sock = sock

    def findDirection(self, coords1, coords2):
        if coords2[0] - coords1[0] ==  1:
            self.r_direction = 1  # right
        if coords2[0] - coords1[0] == -1:
            self.r_direction = 2  #left
        if coords2[1] - coords1[1] ==  1:
            self.r_direction = 3 #up
        if coords2[0] - coords1[0] == -1:
            self.r_direction = 4 #down

        return self.r_direction


    def findCurrentdirectionPosition(self):
        r_sock.sendall(Constants.SERVER_MOVE.encode())
        received_data = r_sock.recv(4096)
        coords1 = extractCoordinates(received_data.decode())

        r_sock.sendall(Constants.SERVER_MOVE.encode())
        received_data = r_sock.recv(4096)
        coords2 = extractCoordinates(received_data.decode())

        self.r_direction = findDirection(coords1, coords2)
        self.r_coords = coords2

    def guideToTarget(self):

        if self.r_coords[0] < 0:
            self.changeDirectionRight()

        while self.r_coords[0] != 0:

            r_sock.sendall(Constants.SERVER_MOVE.encode())
            received_data = self.r_sock.recv(4096)
            coords1 = extractCoordinates(received_data.decode())
            self.r_previousCoords = self.r_coords
            self.r_coords = coords1

        if self.r_coords[0] > 0:
            self.changeDirectionLeft()

        while self.r_coords[0] != 0:
            r_sock.sendall(Constants.SERVER_MOVE.encode())
            received_data = self.r_sock.recv(4096)
            coords1 = extractCoordinates(received_data.decode())
            self.r_previousCoords = self.r_coords
            self.r_coords = coords1

        if self.r_coords[1] < 0:
            self.changeDirectionUp()

        while self.r_coords[1] != 0:
            r_sock.sendall(Constants.SERVER_MOVE.encode())
            received_data = self.r_sock.recv(4096)
            coords1 = extractCoordinates(received_data.decode())
            self.r_previousCoords = self.r_coords
            self.r_coords = coords1

        if self.r_coords[1] > 0:
            self.changeDirectionDown()

        while self.r_coords[1] != 0:
            r_sock.sendall(Constants.SERVER_MOVE.encode())
            received_data = self.r_sock.recv(4096)
            coords1 = extractCoordinates(received_data.decode())
            self.r_previousCoords = self.r_coords
            self.r_coords = coords1

        if self.r_coords == [0, 0]:
            self.r_sock.sendall(Constants.SERVER_PICK_UP.encode())
            received_data = self.r_sock.recv(4096)


    def changeDirectionRight(self):
        if self.r_direction == 1:
            return

        if self.r_direction == 2:
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = self.r_sock.recv(1024)
            # check if we have received ok
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = self.r_sock.recv(1024)
            # check if we have received ok
            self.r_direction = 1
            return

        if self.r_direction == 3:
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = self.r_sock.recv(1024)
            # check if we have received ok
            self.r_direction = 1
            return

        if self.r_direction == 4:
            self.r_sock.sendall(Constants.SERVER_TURN_LEFT.encode())
            received_data = self.r_sock.recv(1024)
            # check if we have received ok
            self.r_direction = 1
            return

    def changeDirectionLeft(self):
        if self.r_direction == 1:
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = self.r_sock.recv(1024)
            # check if we have received ok
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = self.r_sock.recv(1024)
            # check if we have received ok
            self.r_direction = 2
            return

        if self.r_direction == 2:
            return

        if self.r_direction == 3:
            self.r_sock.sendall(Constants.SERVER_TURN_LEFT.encode())
            received_data = self.r_sock.recv(1024)
            # check if we have received ok
            self.r_direction = 2

        if self.r_direction == 4:
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = self.r_sock.recv(1024)
            # check if we have received ok
            self.r_direction = 2

    def changeDirectionUp(self):
        if self.r_direction == 1:
            self.r_sock.sendall(Constants.SERVER_TURN_LEFT.encode())
            received_data = self.r_sock.recv(1024)
            # check if we have received ok
            self.r_direction = 3
            return

        if self.r_direction == 2:
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = self.r_sock.recv(1024)
            # check if we have received ok
            self.r_direction = 3
            return

        if self.r_direction == 3:
            return

        if self.r_direction == 4:
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = self.r_sock.recv(1024)
            # check if we have received ok
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = self.r_sock.recv(1024)
            # check if we have received ok
            self.r_direction = 3
            return

    def changeDirectionDown(self):
        if self.r_direction == 1:
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = self.r_sock.recv(1024)
            # check if we have received ok
            self.r_direction = 4
            return

        if self.r_direction == 2:
            self.r_sock.sendall(Constants.SERVER_TURN_LEFT.encode())
            received_data = self.r_sock.recv(1024)
            # check if we have received ok
            self.r_direction = 4
            return

        if self.r_direction == 3:
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = self.r_sock.recv(1024)
            # check if we have received ok
            self.r_sock.sendall(Constants.SERVER_TURN_RIGHT.encode())
            received_data = self.r_sock.recv(1024)
            # check if we have received ok
            self.r_direction = 4
            return

        if self.r_direction == 4:
            return