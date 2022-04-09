import Constants
import re

robotDirection = 0
robotCoords = []


class robotController:


def extractCoordinates(string):
    return re.findall(r'\d+', string)

def findDirection(coords1, coords2):
    global robotDirection
    if coords2[0] - coords1[0] ==  1:
        robotDirection = 1  # right
    if coords2[0] - coords1[0] == -1:
        robotDirection = 2  #left
    if coords2[1] - coords1[1] ==  1:
        robotDirection = 3 #up
    if coords2[0] - coords1[0] == -1:
        robotDirection = 4 #down

    return robotDirection


def findCurrentdirectionPosition(sock):
    sock.sendall(Constants.SERVER_MOVE.encode())
    received_data = sock.recv(4096)
    coords1 = extractCoordinates(received_data.decode())

    sock.sendall(Constants.SERVER_MOVE.encode())
    received_data = sock.recv(4096)
    coords2 = extractCoordinates(received_data.decode())
    robotDirection = findDirection(coords1, coords2)
    robotCoords = coords2
    return [robotCoords, robotDirection];

def guideToTarget(sock):
