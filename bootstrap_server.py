import logging
from socket import *
import sys


SERVER_PORT = 7734


class Peer(object):
    """docstring for Peer"""

    def __init__(self, host_name, port_number):
        super(Peer, self).__init__()
        self.hostname = host_name
        self.port_number = port_number


class RFC_Index(object):
    """docstring for RFC_Index"""

    def __init__(self, rfc_num, rfc_title, host_name, port_number):
        super(RFC_Index, self).__init__()
        self.rfc_num = rfc_num
        self.rfc_title = rfc_title
        self.hostname = host_name
        self.port_number = port_number


def main():

    logging.info("Starting server at: "+SERVER_PORT)

    # Server socket setup
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', SERVER_PORT))
    server_socket.listen(10)

    logging.info("Waiting for connections...")

    while 1:

        # Fork a process for each client here
        connection_socket, addr = server_socket.accept()
        sentence = connection_socket.recv(1024)
        capitalizedSentence = sentence.upper()
        connection_socket.send(capitalizedSentence)
        connection_socket.close()


if __name__ == '__main__':
    sys.exit(main())