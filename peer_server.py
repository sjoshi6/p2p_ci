import logging
import os
import sys
from threading import Thread
from socket import *
from settings import *
from templates import protocols
from datetime import datetime


# Logger info
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(os.path.basename(__file__))

MY_HOST_NAME = ""
MY_OS_NAME = ""
PSEUDO_NAME = ""
CLIENT_PORT = ""


def handle_peer_request(connection_socket):

    sentence = connection_socket.recv(1024)
    reply_obj = protocols.P2P_Reply_Protocol()

    protocol_obj = protocols.P2P_Request_Protocol()
    protocol_obj.make_dictionary_from_str(sentence.decode("utf-8"))

    if protocol_obj.header_dictionary["PROTOCOL"] != PROTOCOL:

        reply_obj.add_header(PROTOCOL, "404", "Not Found")
        reply = reply_obj.to_str()
        connection_socket.send(bytes(reply, "UTF-8"))
        connection_socket.close()
        return

    else:

        rfc_num = protocol_obj.header_dictionary["RFC_NUM"].lower()
        file_names = os.listdir("data/"+PSEUDO_NAME)

        for file_name in file_names:

            if file_name.startswith(rfc_num):

                with open("data/"+PSEUDO_NAME+"/"+file_name) as f:

                    # Get the data from file & make other params ready for reply
                    data = f.read()
                    last_modified = str(os.path.getmtime("data/"+PSEUDO_NAME+"/"+file_name))
                    content_length = str(os.path.getsize("data/"+PSEUDO_NAME+"/"+file_name))
                    curr_time = str(datetime.now())
                    content_type = "text/text"

                    # Make the reply object ready to be send
                    reply_obj.add_header(PROTOCOL, "200", "OK")
                    reply_obj.add_header_line("Date",curr_time)
                    reply_obj.add_header_line("OS", MY_OS_NAME)
                    reply_obj.add_header_line("Last-Modified", last_modified)
                    reply_obj.add_header_line("Content-Length", content_length)
                    reply_obj.add_header_line("Content-Type", content_type)
                    reply_obj.add_data(data)

                    # Send the response
                    reply = reply_obj.to_str()
                    connection_socket.send(bytes(reply, "UTF-8"))

                    # Close socket after response is sent and return out of thread function
                    connection_socket.close()

                    return


def start_peer_server():

    logging.info("Starting server at: "+str(CLIENT_PORT))

    # Server socket setup
    peer_socket = socket(AF_INET, SOCK_STREAM)
    peer_socket.bind(('', CLIENT_PORT))
    peer_socket.listen(10)
    while 1:
        connection_socket, addr = peer_socket.accept()

        t = Thread(target=handle_peer_request, args=(connection_socket,))
        t.start()


if __name__ == "__main__":

    if len(sys.argv) < 2:
        logging.warning("Incorrect number of arguments; use python peer_server.py <pseudo name>")

    else:

        # Get the host name and update the name with pseudonym
        node_info = os.uname()
        PSEUDO_NAME = sys.argv[1]
        MY_HOST_NAME = node_info[1] + "-" + sys.argv[1]
        MY_OS_NAME = node_info[0] + node_info[2] + node_info[4]

        if PSEUDO_NAME == "peer1":
            CLIENT_PORT = peer1_CLIENT_PORT

        elif PSEUDO_NAME == "peer2":
            CLIENT_PORT = peer2_CLIENT_PORT

        elif PSEUDO_NAME == "peer3":
            CLIENT_PORT = peer3_CLIENT_PORT

        # Start the server for each peer
        start_peer_server()
