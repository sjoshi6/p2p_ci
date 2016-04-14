import logging
import os
import sys
import time
import re
from model import *
from socket import *
from settings import *
from templates import protocols

MY_HOST_NAME = ""
MY_OS_NAME = ""
PSEUDO_NAME = ""
CLIENT_PORT = ""

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
    my_org_files = os.listdir("data/" + PSEUDO_NAME)
    print(my_org_files)
    for file_name in my_org_files:

        file_name_arr = file_name.split("-")
        rfc_num = file_name_arr[0].upper()
        title = file_name_arr[1].upper()

        # Send an add request to the bootstrap server for this RFC
        protocol_obj = protocols.P2S_Protocol()
        protocol_obj.add_header("ADD", rfc_num, PROTOCOL)
        protocol_obj.add_header_line("HOST", MY_HOST_NAME)
        protocol_obj.add_header_line("PORT", str(CLIENT_PORT))
        protocol_obj.add_header_line("TITLE", title)

        send_request_print_reply(client_socket, protocol_obj)

    return


def add_file(client_socket, rfc_num, title):

    protocol_obj = protocols.P2S_Protocol()
    protocol_obj.add_header("ADD", rfc_num, PROTOCOL)
    protocol_obj.add_header_line("HOST", MY_HOST_NAME)
    protocol_obj.add_header_line("PORT", str(CLIENT_PORT))
    protocol_obj.add_header_line("TITLE", title)

    send_request_print_reply(client_socket, protocol_obj)

    return


def recv_timeout(the_socket,timeout=2):

    # make socket non blocking
    the_socket.setblocking(0)

    # total data partwise in an array
    total_data=[];

    # beginning time
    begin=time.time()
    while 1:
        # if you got some data, then break after timeout
        if total_data and time.time()-begin > timeout:
            break

        # if you got no data at all, wait a little longer, twice the timeout
        elif time.time()-begin > timeout*2:
            break

        # recv something
        try:
            data = str(the_socket.recv(8192).decode("utf-8"))

            if data:
                total_data.append(data)
                # change the beginning time for measurement
                begin = time.time()
            else:
                # sleep for sometime to indicate a gap
                time.sleep(0.1)
        except:
            pass

    # join all parts to make final string
    return ''.join(total_data)


def send_request_print_reply(client_socket, protocol_obj):

    # Forward message to server
    request = protocol_obj.to_str()
    client_socket.send(bytes(request, 'UTF-8'))

    # Reply test
    reply = client_socket.recv(1024)
    reply_str = str(reply.decode("utf-8"))
    print("\n" + reply_str + "\n")

    return reply_str


def handle_get(client_socket, rfc_num, title):

    protocol_obj = look_up(rfc_num)
    reply_str = send_request_print_reply(client_socket, protocol_obj)

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

        logging.info("File found at " + host_name + ":" + port_num)
        logging.info("Connecting to the peer to get file")

        peer_protocol_obj = protocols.P2P_Request_Protocol()
        peer_protocol_obj.add_header("GET", rfc_num, PROTOCOL)
        peer_protocol_obj.add_header_line("HOST", MY_HOST_NAME)
        peer_protocol_obj.add_header_line("OS", MY_OS_NAME)

        peer_client_socket = socket(AF_INET, SOCK_STREAM)
        peer_client_socket.connect((host_name, int(port_num)))

        # Forward message to server
        request = peer_protocol_obj.to_str()
        peer_client_socket.send(bytes(request, 'UTF-8'))

        # Reply test
        reply_str = recv_timeout(peer_client_socket,timeout=2)
        print("\n" + reply_str + "\n")

        # Write contents to a file
        with open("data/"+PSEUDO_NAME+"/"+rfc_num.lower()+"-"+title+".txt", 'w') as f:
            f.write(reply_str)

        peer_client_socket.close()

        # Add the file to boot strap server
        add_to_server = input("Do you wish to add this file info to boot strap ? Y/N >")

        if add_to_server == "Y":
            add_file(client_socket, rfc_num, title)

        elif add_to_server == "N":
            logging.info("Skipping the info addition to boot strap server")

        else:
            logging.warning("Incorrect choice made. Not adding the file info to server")

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
        func_name = input("Insert an operation to be performed ADD /GET/ LOOKUP/ LIST > \n")

        # Get is handled differently therefore the outer if statement
        if func_name.startswith("GET"):

            rfc_num = input("> Enter RFC number := ")
            title = input("> Enter RFC title := ")

            if len(rfc_num) < 1 or len(title) < 1:
                logging.warning("Provide document name along with get command")
                continue

            else:
                rfc_num = rfc_num.lstrip().rstrip().upper()
                title = title.lstrip().rstrip()
                logging.info("Received GET for document name:: " + rfc_num)
                handle_get(client_socket, rfc_num, title)

        elif func_name == "EXIT":

            protocol_obj = exit_peer()
            # Forward message to server
            request = protocol_obj.to_str()
            client_socket.send(bytes(request, 'UTF-8'))
            break

        elif func_name.startswith("LOOKUP"):

            rfc_num = input("> Enter RFC number := ")
            title = input("> Enter RFC title := ")

            if len(rfc_num) < 1 or len(title) < 1:
                logging.warning("Provide document name along with get command")
                continue

            else:
                rfc_num = rfc_num.lstrip().rstrip().upper()
                title = title.lstrip().rstrip()
                logging.info("Received LOOKUP for document name:: " + rfc_num)
                protocol_obj = look_up(rfc_num)
                send_request_print_reply(client_socket, protocol_obj)

        elif func_name == "LIST":
            protocol_obj = list_all()
            send_request_print_reply(client_socket, protocol_obj)

    # Close the client socket after while true loop
    client_socket.close()


if __name__ == '__main__':

    if len(sys.argv) < 4:
        logging.warning("Incorrect number of arguments; use python peer.py <pseudo name> <my_ip> <server_ip>")

    else:
        # Get the host name and update the name with pseudonym
        node_info = os.uname()
        #MY_HOST_NAME = node_info[1]# + "-" + sys.argv[1]

        PSEUDO_NAME = sys.argv[1]
        MY_HOST_NAME = sys.argv[2]
        SERVER_HOST_NAME = sys.argv[3]

        MY_OS_NAME = node_info[0] + node_info[2] + node_info[4]

        if PSEUDO_NAME == "peer1":
            CLIENT_PORT = peer1_CLIENT_PORT

        elif PSEUDO_NAME == "peer2":
            CLIENT_PORT = peer2_CLIENT_PORT

        elif PSEUDO_NAME == "peer3":
            CLIENT_PORT = peer3_CLIENT_PORT

        logging.info("New Peer with hostname : " + MY_HOST_NAME + " and PORT " + str(CLIENT_PORT) + " With OS as : " + MY_OS_NAME)

        # Start the peers main function
        main()
