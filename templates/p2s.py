

class P2S_Protocol(object):
    """docstring for P2S_Protocol"""

    def __init__(self):
        super(P2S_Protocol, self).__init__()
        self.header = "method <sp> rfc_number <sp> protocol_ver <cr> <lf>"
        self.content_sample = "field_name <sp> field_value <cr> <lf>"
        self.port_number = "<cr> <lf>"
