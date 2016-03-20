
class Peer(object):
    """docstring for Peer"""

    def __init__(self, host_name, port_number, os_version="nil"):
        super(Peer, self).__init__()
        self.hostname = host_name
        self.port_number = port_number
        self.os_version = os_version

    def to_string(self):
        print(self.hostname+" "+self.port_number+" "+self.os_version)


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
    peer_list = []
    rfc_list = []
    present = {}

    def __init__(self):
        super(BootStrapServer, self).__init__()
