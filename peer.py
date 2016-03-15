import logging
import os
import sys
from socket import *
from settings import *
from templates import protocols

CLIENT_HOST = sys.argv[1]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(os.path.basename(__file__))
logger.info('Starting logs...')


def test_add_data():

    # Create a protocol object using templates
    protocol_obj = protocols.P2S_Protocol()
    protocol_obj.add_header("ADD", "RFC 123", "P2P-CI/2.0")
    protocol_obj.add_header_line("HOST", "thishost.csc.ncsu.edu."+sys.argv[2])
    protocol_obj.add_header_line("PORT", str(CLIENT_PORT))
    protocol_obj.add_header_line("TITLE", "A Preferred Official ICP")
    return protocol_obj


def test_look_up():

    # Create a protocol object using templates
    protocol_obj = protocols.P2S_Protocol()
    protocol_obj.add_header("LOOKUP", "RFC 123", "P2P-CI/1.0")
    protocol_obj.add_header_line("HOST", "thishost.csc.ncsu.edu."+sys.argv[2])
    protocol_obj.add_header_line("PORT", str(CLIENT_PORT))
    protocol_obj.add_header_line("TITLE", "A Preferred Official ICP")
    return protocol_obj


def test_list():

    # Create a protocol object using templates
    protocol_obj = protocols.P2S_Protocol()
    protocol_obj.add_header("LIST", "ALL", "P2P-CI/1.0")
    protocol_obj.add_header_line("HOST", "thishost.csc.ncsu.edu."+sys.argv[2])
    protocol_obj.add_header_line("PORT", str(CLIENT_PORT))
    return protocol_obj


def connect_to_bootstrap():

    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((SERVER_HOST_NAME, SERVER_PORT))

    if sys.argv[1] == "ADD":
        protocol_obj = test_add_data()

    elif sys.argv[1] == "LOOKUP":
        protocol_obj = test_look_up()

    elif sys.argv[1] == "LIST":
        protocol_obj = test_list()

    # Forward message to server
    message = protocol_obj.to_str()
    clientSocket.send(bytes(message, 'UTF-8'))

    # Reply test
    modifiedSentence = clientSocket.recv(1024)
    print(str(modifiedSentence.decode("utf-8")))

    # Close socket
    clientSocket.close()


if __name__ == '__main__':
    logging.info("Called function"+sys.argv[1]+" For host id : "+ sys.argv[2])
    connect_to_bootstrap()