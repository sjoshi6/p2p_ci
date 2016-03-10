from socket import *
from templates import protocols

SERVER_PORT = 7734
SERVER_HOST_NAME = 'localhost'
CLIENT_PORT = 5678


def connect_to_bootstrap():
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((SERVER_HOST_NAME, SERVER_PORT))

    # Create a protcol object using templates
    protocol_obj = protocols.P2S_Protocol()
    protocol_obj.add_header("ADD", "RFC 123", "P2P-CI/1.0")
    protocol_obj.add_header_line("HOST", "thishost.csc.ncsu.edu")
    protocol_obj.add_header_line("PORT", str(CLIENT_PORT))
    protocol_obj.add_header_line("TITLE", "A Preferred Official ICP")

    # Forward message to server
    message = protocol_obj.to_str()
    clientSocket.send(bytes(message, 'UTF-8'))

    # Reply test
    modifiedSentence = clientSocket.recv(1024)
    print(str(modifiedSentence.decode("utf-8")))

    # Close socket
    clientSocket.close()


if __name__ == '__main__':
    connect_to_bootstrap()