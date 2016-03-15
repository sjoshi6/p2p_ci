
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