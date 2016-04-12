import re


class P2S_Protocol(object):
    """docstring for P2S_Protocol"""

    def __init__(self):
        super(P2S_Protocol, self).__init__()
        self.header = ""
        self.header_lines = []
        self.header_dictionary = {}  # Used to create object from str
        self.trailer = "<cr> <lf>"

    def add_header(self, method, rfc_number, protocol_ver):
        self.header = method+" <sp> "+rfc_number+" <sp> "+protocol_ver+" <cr> <lf>"

    def add_header_line(self, field_name, field_value):
        header_line = field_name+" <sp> "+field_value+" <cr> <lf>"
        self.header_lines.append(header_line)

    def to_str(self):
        message = self.header

        for line in self.header_lines:
            message = message + "\n" + line

        message = message + "\n" + self.trailer
        return message

    def make_dictionary_from_str(self, message):

        lines = message.split("\n")

        # process header from str and add to dictionary
        header_str = lines[0]
        data = re.search('(.*)<sp>(.*)<sp>(.*)<cr> <lf>', header_str)

        method = data.group(1).lstrip().rstrip()
        rfc_num = data.group(2).lstrip().rstrip()
        protocol = data.group(3).lstrip().rstrip()

        self.header_dictionary["METHOD"] = method
        self.header_dictionary["RFC_NUM"] = rfc_num
        self.header_dictionary["PROTOCOL"] = protocol

        # process each extra header line
        for i in range(1, len(lines)-1):

            line = lines[i]
            data = re.search('(.*)<sp>(.*)<cr> <lf>', line)

            name = data.group(1).lstrip().rstrip()
            value = data.group(2).lstrip().rstrip()

            self.header_dictionary[name] = value


class S2P_Protocol(object):
    """docstring for S2P_Protocol"""

    def __init__(self):
        super(S2P_Protocol, self).__init__()
        self.header = ""
        self.header_lines = []
        self.header_dictionary = {}  # Used to create object from str
        self.trailer = "<cr> <lf>"

    def add_header(self,protocol_ver, reply, desc):
        self.header = protocol_ver+" <sp> "+reply+" <sp> "+desc+" <cr> <lf>"

    def add_header_line(self, rfc_num, rfc_title, host_name, host_port):
        self.header_lines.append(rfc_num + " <sp> "+rfc_title+" <sp> "+host_name+" <sp> "+host_port+" <cr> <lf>")

    def to_str(self):
        message = self.header

        for line in self.header_lines:
            message = message + "\n" + line

        message = message + "\n" + self.trailer
        return message


class P2P_Request_Protocol(object):
    """docstring for P2P_Request_Protocol"""

    def __init__(self):
        super(P2P_Request_Protocol, self).__init__()
        self.header = ""
        self.header_lines = []
        self.header_dictionary = {}  # Used to create object from str
        self.trailer = "<cr> <lf>"

    def add_header(self,method, rfc_num, proto_ver):
        self.header = method+" <sp> "+rfc_num+" <sp> "+proto_ver+" <cr> <lf>"

    def add_header_line(self, field, value):
        self.header_lines.append(field+" <sp> "+value+" <cr> <lf>")

    def to_str(self):
        message = self.header

        for line in self.header_lines:
            message = message + "\n" + line

        message = message + "\n" + self.trailer
        return message

    def make_dictionary_from_str(self, message):

        lines = message.split("\n")

        # process header from str and add to dictionary
        header_str = lines[0]
        data = re.search('(.*)<sp>(.*)<sp>(.*)<cr> <lf>', header_str)

        method = data.group(1).lstrip().rstrip()
        rfc_num = data.group(2).lstrip().rstrip()
        protocol = data.group(3).lstrip().rstrip()

        self.header_dictionary["METHOD"] = method
        self.header_dictionary["RFC_NUM"] = rfc_num
        self.header_dictionary["PROTOCOL"] = protocol

        # process each extra header line
        for i in range(1, len(lines)-1):

            line = lines[i]
            data = re.search('(.*)<sp>(.*)<cr> <lf>', line)

            name = data.group(1).lstrip().rstrip()
            value = data.group(2).lstrip().rstrip()

            self.header_dictionary[name] = value


class P2P_Reply_Protocol(object):
    """docstring for P2P_Reply_Protocol"""

    def __init__(self):
        super(P2P_Reply_Protocol, self).__init__()
        self.header = ""
        self.header_lines = []
        self.header_dictionary = {}  # Used to create object from str
        self.trailer = "<cr> <lf>"
        self.data = ""

    def add_header(self, protocol_ver, reply, desc):
        self.header = protocol_ver+" <sp> "+reply+" <sp> "+desc+" <cr> <lf>"

    def add_header_line(self, key, value):
        self.header_lines.append(key + " <sp> "+value+" <cr> <lf>")

    def add_data(self, data):

        self.data = data

    def to_str(self):
        message = self.header

        for line in self.header_lines:
            message = message + "\n" + line

        message = message + "\n" + self.trailer + "\n"
        message += self.data

        return message
