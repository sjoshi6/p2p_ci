import logging
import os
import sys
import re
import platform
from model import *
from socket import *
from settings import *
from templates import protocols

MY_HOST_NAME = ""
MY_OS_NAME = ""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(os.path.basename(__file__))

logger.info('Starting logs...')


def look_up(rfc_num):

    # Create a protocol object using templates
    protocol_obj = protocols.P2S_Protocol()
    protocol_obj.add_header("LOOKUP", rfc_num, "P2P-CI/1.0")
    protocol_obj.add_header_line("HOST", MY_HOST_NAME)
    protocol_obj.add_header_line("PORT", str(CLIENT_PORT))
    protocol_obj.add_header_line("TITLE", "A Preferred Official ICP")
    return protocol_obj


def list_all():

    # Create a protocol object using templates
    protocol_obj = protocols.P2S_Protocol()
    protocol_obj.add_header("LIST", "ALL", "P2P-CI/1.0")
    protocol_obj.add_header_line("HOST", MY_HOST_NAME)
    protocol_obj.add_header_line("PORT", str(CLIENT_PORT))
    return protocol_obj


def exit_peer():

    # Create a protocol object using templates
    protocol_obj = protocols.P2S_Protocol()
    protocol_obj.add_header("EXIT", "*", "P2P-CI/1.0")
    protocol_obj.add_header_line("HOST", MY_HOST_NAME)
    protocol_obj.add_header_line("PORT", str(CLIENT_PORT))
    return protocol_obj


def connect_to_bootstrap():

    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((SERVER_HOST_NAME, SERVER_PORT))
    return client_socket


def add_file_chunk_info(client_socket):

    # Get all files from the data
    my_org_files = os.listdir("data")

    for file_name in my_org_files:

        file_name_arr = file_name.split("-")
        rfc_num = file_name_arr[0].upper()
        title = file_name_arr[1].upper()

        # Send an add request to the bootstrap server for this RFC
        protocol_obj = protocols.P2S_Protocol()
        protocol_obj.add_header("ADD", rfc_num, "P2P-CI/1.0")
        protocol_obj.add_header_line("HOST", MY_HOST_NAME)
        protocol_obj.add_header_line("PORT", str(CLIENT_PORT))
        protocol_obj.add_header_line("TITLE", title)
        request = protocol_obj.to_str()
        client_socket.send(bytes(request, 'UTF-8'))

        # Reply for this added RFC index
        reply = client_socket.recv(1024)
        reply_str = str(reply.decode("utf-8"))
        logging.info(reply_str)

    return


def connect_to_peer():
    pass


#def send_request_print_reply()

def handle_get(client_socket, rfc_num):

    protocol_obj = look_up(rfc_num)

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
        myself_peer = Peer(MY_HOST_NAME, str(CLIENT_PORT), MY_OS_NAME)

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

    # Establish a permanent connection to bootstrap
    logging.info("Connecting to server socket...")
    client_socket = connect_to_bootstrap()

    logging.info("Connection success")

    logging.info("Uploading my file chuncks info to bootstrap server")
    add_file_chunk_info(client_socket)

    logging.info("Peer accepting functions... ")

    while True:
        func_name = input("Insert an operation to be performed ADD /GET/ LOOKUP/ LIST \n")

        # Get is handled differently therefore the outer if statement
        if func_name.startswith("GET"):

            cmd_arr = func_name.split(" ")
            if len(cmd_arr) <= 1:
                logging.warning("Provide document name along with get command")
                continue

            else:
                doc_name = cmd_arr[1].lstrip().rstrip()
                logging.info("Received GET for document name:: " + doc_name)
                handle_get(client_socket, doc_name)

        elif func_name == "EXIT":
            protocol_obj = exit_peer()
            # Forward message to server
            request = protocol_obj.to_str()
            client_socket.send(bytes(request, 'UTF-8'))
            break

        elif func_name.startswith("LOOKUP"):

            cmd_arr = func_name.split(" ")
            if len(cmd_arr) <= 1:
                logging.warning("Provide document name along with get command")
                continue

            else:
                doc_name = cmd_arr[1].lstrip().rstrip()
                logging.info("Received LOOKUP for document name:: " + doc_name)
                protocol_obj = look_up(doc_name)

                # Forward message to server
                request = protocol_obj.to_str()
                client_socket.send(bytes(request, 'UTF-8'))

                # Reply test
                reply = client_socket.recv(1024)
                reply_str = str(reply.decode("utf-8"))
                print(reply_str)

        elif func_name == "LIST":
            protocol_obj = list_all()

            # Forward message to server
            request = protocol_obj.to_str()
            client_socket.send(bytes(request, 'UTF-8'))

            # Reply test
            reply = client_socket.recv(1024)
            reply_str = str(reply.decode("utf-8"))
            print(reply_str)

    # Close the client socket after while true loop
    client_socket.close()


if __name__ == '__main__':

    if len(sys.argv) < 2:
        logging.warning("Incorrect number of arguments; use python peer.py <pseudo name>")

    else:
        # Get the host name and update the name with pseudonym
        node_info = os.uname()
        MY_HOST_NAME = node_info[1] + "-" + sys.argv[1]
        MY_OS_NAME = node_info[0] + node_info[2] + node_info[4]

        logging.info("New Peer with hostname : " + MY_HOST_NAME + " With OS as : " + MY_OS_NAME)

        # Start the peers main function
        main()
