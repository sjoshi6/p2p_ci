import logging
import os
import sys
from model import *
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


def look_up(rfc_num):

    # Create a protocol object using templates
    protocol_obj = protocols.P2S_Protocol()
    protocol_obj.add_header("LOOKUP", rfc_num, "P2P-CI/1.0")
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

    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((SERVER_HOST_NAME, SERVER_PORT))
    return client_socket


def connect_to_peer():
    pass


def handle_get(client_socket, rfc_num):

    # look up for the rfc in bootstrap server
    protocol_obj = look_up(rfc_num)
    request = protocol_obj.to_str()
    client_socket.send(bytes(request, 'UTF-8'))

    # Capture the server reply
    reply = client_socket.recv(1024)
    reply_str = str(reply.decode("utf-8"))

    # Unwrap the string to get details about the peer
    os_version = "" # find from library
    host_name = "" # extract from the reply
    port_num = 0 # extract from the reply
    peer = Peer(host_name, port_num, os_version)

    # Connect to the peer and send get request
    peer.get(rfc_num)


def main():

    # Establish a permanent connection to bootstrap
    client_socket = connect_to_bootstrap()

    if sys.argv[1] == "GET":

        # If get is received perform all query ops and connect to peer + get data of the rfc
        handle_get(client_socket, "RFC 123")

    else:

        # one of the test data cases
        if sys.argv[1] == "ADD":
            protocol_obj = test_add_data()

        elif sys.argv[1] == "LOOKUP":
            protocol_obj = look_up("RFC 123")

        elif sys.argv[1] == "LIST":
            protocol_obj = test_list()

        # Forward message to server
        request = protocol_obj.to_str()
        client_socket.send(bytes(request, 'UTF-8'))

        # Reply test
        reply = client_socket.recv(1024)
        reply_str = str(reply.decode("utf-8"))
        print(reply_str)


if __name__ == '__main__':
    logging.info("Called function"+sys.argv[1]+" For host id : "+ sys.argv[2])
    main()