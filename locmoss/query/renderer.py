

class TerminalRenderer(object):
    def __init__(self, width=80):
        self.width = width
        self.content = []

    def add_header(self, s):
        w = self.width - 2
        pad_len = (w - len(s)) // 2
        padding = " " * pad_len
        end_padding = " " * (w - len(s) - pad_len)
        self.content.append("/{}+".format("-" * w))
        self.content.append("|{}{}{}|".format(padding, s, end_padding))
        self.content.append("+{}/".format("-" * w))

    def add_raw(self, l):
        self.content.append(l)

    def render(self):
        for line in self.content:
            print(line)
