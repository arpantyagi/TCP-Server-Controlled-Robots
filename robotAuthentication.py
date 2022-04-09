import Constants
import helpers

"""
This function will get a socket object, parse the messages received 
check username 


"""
def robotAuthentication(sock):

    # Get username
    received_data = sock.recv(4096)
    userName = received_data[:-2].decode()
    if not received_data:
        sock.close()

    sock.sendall(Constants.SERVER_KEY_REQUEST.encode())



    # Get which key to use
    received_data = sock.recv(4096)
    key = int(received_data[:-2].decode())
    if not received_data:
        sock.close()

    if (int(key) > 4 or int(key) < 0):
        sock.sendall(Constants.SERVER_KEY_OUT_OF_RANGE_ERROR.encode())
    hash = helpers.calculateHash(userName, key)
    sock.sendall(f"{str(hash)}\a\b".encode())



    # Check hash from client side
    received_data = sock.recv(4096)
    recvHash = int(received_data[:-2].decode())

    if( recvHash != helpers.calculateHash(userName, key, True)):
        sock.sendall(Constants.SERVER_LOGIN_FAILED.encode())
        helpers.closeConnection(sock)

    sock.sendall(Constants.SERVER_OK.encode())

    print("Authentication Complete!")
    #helpers.closeConnection(sock)

