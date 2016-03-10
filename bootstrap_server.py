import logging
import os
from socket import *
import sys
from templates import protocols


# constants
SERVER_PORT = 7734

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(os.path.basename(__file__))
logger.info('Starting logs...')


class Peer(object):
    """docstring for Peer"""

    def __init__(self, host_name, port_number):
        super(Peer, self).__init__()
        self.hostname = host_name
        self.port_number = port_number

    def to_string(self):
        print(self.hostname+" "+self.port_number)


class RFC_Index(object):
    """docstring for RFC_Index"""

    def __init__(self, rfc_num, rfc_title, host_name, port_number):
        super(RFC_Index, self).__init__()
        self.rfc_num = rfc_num
        self.rfc_title = rfc_title
        self.hostname = host_name
        self.port_number = port_number

    def to_string(self):
        print(self.rfc_num+" "+self.rfc_title+" "+self.hostname+" "+self.port_number)


class BootStrapServer(object):
    """docstring for BootStrapServer"""

    def __init__(self):
        super(BootStrapServer, self).__init__()
        self.peer_list = []
        self.rfc_list = []
        self.present = {}


def addHandler(bs_server, connection_socket, protocol_obj, reply_obj):


    # Adding the peer to the dictionary
    host_name = protocol_obj.header_dictionary["HOST"]
    port_num = protocol_obj.header_dictionary["PORT"]

    if protocol_obj.header_dictionary["HOST"] not in bs_server.present:

        try:
            logging.info("Peer not present in the system")
            logging.info("adding peer...")

            # Creating peer object & appending to the list
            peer = Peer(host_name, port_num)
            bs_server.present[host_name] = True
            bs_server.peer_list.append(peer)

        except:
            reply_obj.add_header("P2P-CI/1.0", "400", "Bad Request")
            reply = reply_obj.to_str()
            connection_socket.send(bytes(reply, "UTF-8"))
    else:
        logging.info("Peer present in the system")
        logging.info("Continue operations...")
        pass

    # RFC index creation
    rfc_num = protocol_obj.header_dictionary["RFC_NUM"]
    title = protocol_obj.header_dictionary["TITLE"]
    rfc_index = RFC_Index(rfc_num,title, host_name, port_num)

    # RFC added to list
    bs_server.rfc_list.append(rfc_index)

    reply_obj.add_header("P2P-CI/1.0", "200", "OK")
    reply = reply_obj.to_str()
    connection_socket.send(bytes(reply, "UTF-8"))
    return bs_server


def test_print(bs_server):

    print("############")
    print(bs_server.present)
    print("############")
    print(bs_server.peer_list[0].to_string())
    for rfc in bs_server.rfc_list:
        rfc.to_string()

    print("############")


def main():

    bs_server = BootStrapServer()
    logging.info("Starting server at: "+str(SERVER_PORT))

    # Server socket setup
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', SERVER_PORT))
    server_socket.listen(10)

    logging.info("Waiting for connections...")

    while 1:

        # Fork a process for each client here
        connection_socket, addr = server_socket.accept()
        sentence = connection_socket.recv(1024)
        reply_obj = protocols.S2P_Protocol()

        protocol_obj = protocols.P2S_Protocol()
        protocol_obj.make_dictionary_from_str(sentence.decode("utf-8"))
        print(protocol_obj.header_dictionary)

        if protocol_obj.header_dictionary["METHOD"] == "ADD":

            logging.info("Received Add request")
            bs_server = addHandler(bs_server, connection_socket, protocol_obj, reply_obj)

        elif protocol_obj.header_dictionary["METHOD"] == "LIST":

            logging.info("Received LIST request")

        else:

            logging.warning("Incorrect method choice")
            pass

        connection_socket.close()

        # Test purpose
        test_print(bs_server)

if __name__ == '__main__':
    sys.exit(main())