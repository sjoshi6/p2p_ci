from socket import *
from templates import *

SERVER_PORT = 7734
SERVER_HOST_NAME = 'localhost'


def connect_to_bootstrap():
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((SERVER_HOST_NAME, SERVER_PORT))
    sentence = input('Input lowercase sentence:')
    clientSocket.send(bytes(sentence, 'UTF-8'))
    modifiedSentence = clientSocket.recv(1024)
    print('SERVER REPLY: ', str(modifiedSentence.decode("utf-8") ))
    clientSocket.close()


if __name__ == '__main__':
    connect_to_bootstrap()