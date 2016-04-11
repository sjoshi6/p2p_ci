import logging
import os
import sys
import re
import platform
from model import *
from socket import *
from settings import *
from templates import protocols


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(os.path.basename(__file__))
logger.info('Starting logs...')


def test_add_data():

    # Create a protocol object using templates
    protocol_obj = protocols.P2S_Protocol()
    protocol_obj.add_header("ADD", "RFC 123", "P2P-CI/1.0")
    protocol_obj.add_header_line("HOST", sys.argv[2])
    protocol_obj.add_header_line("PORT", str(CLIENT_PORT))
    protocol_obj.add_header_line("TITLE", "A Preferred Official ICP")
    return protocol_obj


def look_up(rfc_num):

    # Create a protocol object using templates
    protocol_obj = protocols.P2S_Protocol()
    protocol_obj.add_header("LOOKUP", rfc_num, "P2P-CI/1.0")
    protocol_obj.add_header_line("HOST", sys.argv[2])
    protocol_obj.add_header_line("PORT", str(CLIENT_PORT))
    protocol_obj.add_header_line("TITLE", "A Preferred Official ICP")
    return protocol_obj


def test_list():

    # Create a protocol object using templates
    protocol_obj = protocols.P2S_Protocol()
    protocol_obj.add_header("LIST", "ALL", "P2P-CI/1.0")
    protocol_obj.add_header_line("HOST", sys.argv[2])
    protocol_obj.add_header_line("PORT", str(CLIENT_PORT))
    return protocol_obj


def connect_to_bootstrap():

    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((SERVER_HOST_NAME, SERVER_PORT))
    return client_socket


def connect_to_peer():
    pass


def handle_get(client_socket, rfc_num):

    protocol_obj = look_up("RFC 123")

    # Forward message to server
    request = protocol_obj.to_str()
    client_socket.send(bytes(request, 'UTF-8'))

    # Reply test
    reply = client_socket.recv(1024)
    reply_str = str(reply.decode("utf-8"))

    # extract response code
    reply_arr = reply_str.split('\n')
    header = reply_arr[0]
    data = re.search('(.*)<sp>(.*)<sp>(.*)<cr> <lf>', header)
    response_code = data.group(2).lstrip().rstrip()

    if response_code == "200":

        # Unwrap the string to get details about the peer
        first_match = reply_arr[1]
        data = re.search('(.*)<sp>(.*)<sp>(.*)<sp>(.*)<cr> <lf>', first_match)
        host_name = data.group(3).lstrip().rstrip()
        port_num = data.group(4).lstrip().rstrip()

        # create the info object for the peer holding the file
        file_owner_peer = Peer(host_name, port_num, "")

        # create an object with my own host / port / os version
        os_version = platform.system() + " " + platform.release()
        myself_peer = Peer("host.ncsu.edu", str(CLIENT_PORT), os_version)

        # Connect to the peer and send get request
        logging.info("###################################")
        logging.info("File owners info...")
        logging.info(file_owner_peer.to_string())

        logging.info("My Info...")
        logging.info(myself_peer.to_string())
        logging.info("###################################")

    elif response_code == "404":
        logging.warning("The page that we tried to look up is missing")
        return None


def main():

    if len(sys.argv) < 3:
        logging.warning("Incorrect number of arguments; use python peer.py <pseudo name> <hostid>")
    # Establish a permanent connection to bootstrap
    logging.info("Connecting to server socket...")
    client_socket = connect_to_bootstrap()

    logging.info("Connection success. Accepting peer functions now...")

    while True:
        logging.info(client_socket)
        func_name = input("Insert an operation to be performed ADD /GET/ LOOKUP/ LIST \n")

        if func_name.startswith("GET"):

            # If get is received perform all query ops and connect to peer + get data of the rfc
            handle_get(client_socket, "RFC 123")

        else:

            # one of the test data cases
            if func_name == "ADD":
                protocol_obj = test_add_data()

            elif func_name == "LOOKUP":
                protocol_obj = look_up("RFC 123")

            elif func_name == "LIST":
                protocol_obj = test_list()

            # Forward message to server
            request = protocol_obj.to_str()
            client_socket.send(bytes(request, 'UTF-8'))

            # Reply test
            reply = client_socket.recv(1024)
            reply_str = str(reply.decode("utf-8"))
            print(reply_str)


if __name__ == '__main__':
    logging.info("Pseudo name :"+sys.argv[1]+" For host id : " + sys.argv[2])
    main()
