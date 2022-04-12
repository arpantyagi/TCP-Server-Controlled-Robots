authenticationKeys = { 0 : (23019, 32037),
                       1 : (32037, 29295),
                       2 : (18789, 13603),
                       3 : (16443, 29533),
                       4 : (18189, 21952)}


import Constants
import helpers

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

    def closeConnection(self):
        print('Client disconnected:', sock.getpeername())
        self.r_sock.close()

    def calculateHash(self, client=False):
        hashSum = 0
        for char in self.r_username:
            hashSum = hashSum + ord(char)

        if (client):
            return ((hashSum * 1000) % 65536 + authenticationKeys[self.r_key][1]) % 65536
        result = ((hashSum * 1000) % 65536 + authenticationKeys[self.r_key][0]) % 65536
        return result

    # Possibly Generator that should
    def receiveMessage(self):

        while True:
            received_data = self.r_sock.recv(4096).decode()
            self.r_pipe.append(received_data)

            messageEndIndex = self.r_pipe.find('\a\b')
            if messageEndIndex == -1:
                pass
            else:
                nextMessage = self.r_pipe[:messageEndIndex]
                self.r_pipe = self.r_pipe[messageEndIndex+1]
                print(nextMessage)
                return nextMessage


    def authenticateConnection(self):

        # Receive Username
        self.r_username = self.receiveMessage()
        if not self.r_username:
            self.closeConnection()

        # Request Key
        self.r_sock.sendall(Constants.SERVER_KEY_REQUEST.encode())

        # Receive Keys
        self.r_key = self.receiveMessage()
        if not self.r_key:
            self.closeConnection()
        if int(self.r_key) > 4 or int(self.r_key) < 0:
            self.r_sock.sendall(Constants.SERVER_KEY_OUT_OF_RANGE_ERROR)

        # Get Hash
        self.r_hash = self.calculateHash()
        self.r_sock.sendall(f"{str(hash)}\a\b".encode())

        #Check Client Hash
        self.r_clientHash = int(self.receiveMessage())

        if self.r_clientHash != self.calculateHash(client=True):
            self.r_sock.sendall(Constants.SERVER_LOGIN_FAILED.encode())
            self.closeConnection()
        else:
            self.r_sock.sendall(Constants.SERVER_OK.encode())
        print("Authentication Complete!")
