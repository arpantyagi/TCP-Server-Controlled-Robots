authenticationKeys = { 0 : (23019, 32037),
                       1 : (32037, 29295),
                       2 : (18789, 13603),
                       3 : (16443, 29533),
                       4 : (18189, 21952)}

def closeConnection(sock):
    print('Client disconnected:', sock.getpeername())
    sock.close()

def calculateHash(userName, key, client=False):
    sum = 0
    for char in userName:
        sum = sum + ord(char)

    if(client):
        return ((sum * 1000) % 65536 + authenticationKeys[key][1]) % 65536
    return ((sum * 1000) %  65536 + authenticationKeys[key][0]) % 65536



