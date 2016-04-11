import logging
import os
from socket import *
from settings import *
import sys
from templates import protocols
from model import *
from threading import Thread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(os.path.basename(__file__))
logger.info('Starting logs...')

bs_server = BootStrapServer()


def check_protocol(protocol_obj):

    """
    Checks the protocol of the incoming request
    :param protocol_obj: P2S protocol object
    :return: boolean
    """

    if protocol_obj.header_dictionary["PROTOCOL"] == PROTOCOL:
        logging.info("Protocol check passed")
        return True
    else:
        logging.warning("Protocol check failed")
        return False


def add_handler(bs_server, connection_socket, protocol_obj, reply_obj):

    """
    Add Handler is used to handler add request to the server
    :param bs_server: bootstrap server object
    :param connection_socket: connection socket for handling client request
    :param protocol_obj: object of p2s protocol
    :param reply_obj: response object
    :return: bootstrap server object
    """

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


def lookup_handler(bs_server, connection_socket, protocol_obj, reply_obj):

    """
    Handles look up request by clients
    :param bs_server: boot strap object
    :param connection_socket: connection socket for client request
    :param protocol_obj: p2s protocol object
    :param reply_obj: object to send reply
    :return: None
    """

    rfc_num = protocol_obj.header_dictionary["RFC_NUM"]
    title = protocol_obj.header_dictionary["TITLE"]

    rows = []
    for record in bs_server.rfc_list:
        if record.rfc_num == rfc_num and record.rfc_title == title:
            rows.append(record)

    if len(rows) < 1:
        reply_obj.add_header("P2P-CI/1.0", "404", "Not Found")
        reply = reply_obj.to_str()
        connection_socket.send(bytes(reply, "UTF-8"))

    else:
        reply_obj.add_header("P2P-CI/1.0", "200", "OK")

        for record in rows:
            reply_obj.add_header_line(record.rfc_num, record.rfc_title, record.hostname, record.port_number)

        reply = reply_obj.to_str()
        connection_socket.send(bytes(reply, "UTF-8"))


def list_handler(bs_server, connection_socket, reply_obj):

    """
    Handles list request by clients
    :param bs_server: boot strap object
    :param connection_socket: connection socket for client request
    :param protocol_obj: p2s protocol object
    :param reply_obj: object to send reply
    :return: None
    """

    try:
        reply_obj.add_header("P2P-CI/1.0", "200", "OK")

        for record in bs_server.rfc_list:
            reply_obj.add_header_line(record.rfc_num, record.rfc_title, record.hostname, record.port_number)

        reply = reply_obj.to_str()
        connection_socket.send(bytes(reply, "UTF-8"))

    except:
        reply_obj.add_header("P2P-CI/1.0", "400", "Bad Request")
        reply = reply_obj.to_str()
        connection_socket.send(bytes(reply, "UTF-8"))


def test_print(bs_server):

    print("############")
    print(bs_server.present)
    print("############")
    for rfc in bs_server.rfc_list:
        rfc.to_string()

    print("############")


# Used to process one clients requests
def process_requests(connection_socket, bs_server):

    while 1:
        sentence = connection_socket.recv(1024)
        reply_obj = protocols.S2P_Protocol()

        protocol_obj = protocols.P2S_Protocol()
        protocol_obj.make_dictionary_from_str(sentence.decode("utf-8"))
        print(protocol_obj.header_dictionary)

        if check_protocol(protocol_obj):

            if protocol_obj.header_dictionary["METHOD"] == "ADD":

                logging.info("Received ADD request")
                add_handler(bs_server, connection_socket, protocol_obj, reply_obj)

            elif protocol_obj.header_dictionary["METHOD"] == "LOOKUP":

                logging.info("Received LOOKUP request")
                lookup_handler(bs_server, connection_socket, protocol_obj, reply_obj)

            elif protocol_obj.header_dictionary["METHOD"] == "LIST":

                logging.info("Received LIST request")
                list_handler(bs_server,connection_socket,reply_obj)

            else:

                logging.warning("Incorrect method choice")
                pass

        else:

            reply_obj.add_header("P2P-CI/1.0", "505", "P2P-CI Version Not Supported")
            reply = reply_obj.to_str()
            connection_socket.send(bytes(reply, "UTF-8"))

    connection_socket.close()


def main():

    logging.info("Starting server at: "+str(SERVER_PORT))

    # Server socket setup
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', SERVER_PORT))
    server_socket.listen(10)

    while 1:

        logging.info("Waiting for connections...")
        connection_socket, addr = server_socket.accept()

        logging.info("Connected from "+str(addr))
        t = Thread(target=process_requests, args=(connection_socket, bs_server))
        t.start()

    # Close the server socket
    server_socket.close()


if __name__ == '__main__':
    main()
