from abc import ABCMeta, abstractmethod
from .report import Header, ReportList, Table


class Renderer(object, metaclass=ABCMeta):
    def __call__(self, report):
        for block in report:
            if isinstance(block, Header):
                self.render_header(block)
            elif isinstance(block, ReportList):
                self.render_list(block)
            elif isinstance(block, Table):
                self.render_table(block)
            else:
                self.render_raw(block)

    @abstractmethod
    def render_header(self, header):
        pass

    @abstractmethod
    def render_raw(self, s):
        pass

    @abstractmethod
    def render_list(self, report_list):
        pass

    @abstractmethod
    def render_table(self, table):
        pass



class TerminalRenderer(Renderer):
    def __init__(self, width=80):
        self.width = width
        self.content = []

    def render_header(self, header):
        w = self.width - 2
        pad_len = (w - len(header)) // 2
        padding = " " * pad_len
        end_padding = " " * (w - len(header) - pad_len)
        print("/{}+".format("-" * w))
        print("|{}{}{}|".format(padding, header, end_padding))
        print("+{}/".format("-" * w))
        return self

    def render_raw(self, s):
        print(s)

    def render_list(self, report_list):
        if report_list.headline is not None:
            print(report_list.headline)
        for li in report_list:
            print(" - {}".format(li))


    def render_table(self, table):
        widths = [x+2 for x in table.column_widths]
        def row2str(row):
            s = ""
            for w, c in zip(widths, row):
                s += ("| " + str(c).ljust(w-1))
            return s + "|"

        hline = ""
        for width in widths:
            hline += ("+" + "-"*width)
        hline += "+"



        print(hline)
        if table.header:
            print(row2str(table.header))
            print(hline)
        for row in table:
            print(row2str(row))
        print(hline)
        if table.footer:
            print(row2str(table.footer))
            print(hline)


