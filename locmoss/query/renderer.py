import os
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager

from .report import Header, ReportList, Table, Anchor, Reference, Description, \
    Section, SubSection, Snippet, Anchorable, Newline


class Renderer(object, metaclass=ABCMeta):
    @abstractmethod
    def display(self, s, **kwargs):
        pass

    def __call__(self, report):
        if report is not None:
            for block in report:
                self.display(self.dispatch(block))


    def dispatch(self, block):
        if isinstance(block, Newline):
            return self.render_newline(block)
        elif isinstance(block, Header):
            return self.render_header(block)
        elif isinstance(block, ReportList):
            return self.render_list(block)
        elif isinstance(block, Table):
            return self.render_table(block)
        elif isinstance(block, Anchor):
            return self.render_anchor(block)
        elif isinstance(block, Reference):
            return self.render_reference(block)
        elif isinstance(block, Description):
            return self.render_description(block)
        elif isinstance(block, Section):
            return self.render_section(block)
        elif isinstance(block, SubSection):
            return self.render_subsection(block)
        elif isinstance(block, Snippet):
            return self.render_snippet(block)
        elif isinstance(block, Anchorable):
            return self.render_anchorable(block)
        else:
            return self.render_raw(block)

    # -------------------------------- IN LINE --------------------------------
    @abstractmethod
    def render_newline(self, _):
        return ""

    @abstractmethod
    def render_raw(self, s):
        return ""

    @abstractmethod
    def render_anchor(self, anchor):
        return ""

    @abstractmethod
    def render_anchorable(self, anchorable):
        return ""

    @abstractmethod
    def render_reference(self, ref):
        return ""

    # --------------------------------- BLOCK ---------------------------------
    @abstractmethod
    def render_header(self, header):
        return ""

    @abstractmethod
    def render_list(self, report_list):
        return ""

    @abstractmethod
    def render_table(self, table):
        return ""

    @abstractmethod
    def render_description(self, description):
        return ""

    @abstractmethod
    def render_section(self, section):
        return ""

    @abstractmethod
    def render_subsection(self, subsection):
        return ""

    @abstractmethod
    def render_snippet(self, snippet):
        return ""


@contextmanager
def increment_width(terminal_renderer, delta):
    original_width = terminal_renderer.width
    try:
        new_width = original_width + delta
        terminal_renderer.width = new_width
        yield new_width
    finally:
        terminal_renderer.width = original_width



class TerminalRenderer(Renderer):
    def __init__(self, width=80, anchor_max_length=12):
        self.width = width
        self.anchor_max_length = anchor_max_length

    def display(self, s, **kwargs):
        print(s, **kwargs)

    def _justify(self, left, to_justify, boundaries=0):
        pad = self.width - len(left) - len(to_justify) - boundaries
        if pad < 1:
            pad = 1
        return "{}{}{}".format(left, " " * pad, to_justify)

    def _multiline(self, *lines):
        return os.linesep.join(lines)

    def render_newline(self, _):
        return os.linesep

    def render_raw(self, s):
        return s

    def render_anchor(self, anchor):
        a_str = anchor.as_hash_str()[:self.anchor_max_length-1]
        return "#{}".format(a_str)

    def render_anchorable(self, anchorable):
        a_str = self.render_anchor(anchorable.anchor)
        s = str(anchorable)
        return "{} ({})".format(s, a_str)

    def render_reference(self, ref):
        return self.render_anchorable(ref)


    def render_header(self, header):
        w = self.width - 2
        pad_len = (w - len(header)) // 2
        padding = " " * pad_len
        end_padding = " " * (w - len(header) - pad_len)
        l1 = "/{}+".format("-" * w)
        l2 = "|{}{}".format(padding, header)
        l2 = self._justify(l2, self.render_anchor(header.anchor), 2)
        l2 += " |"
        l3 = "+{}/".format("-" * w)
        return self._multiline(l1, l2, l3)


    def render_section(self, section):
        l1 = self._justify(str(section), self.render_anchor(section.anchor))
        return self._multiline(l1, "="*self.width)


    def render_subsection(self, subsection):
        l1 = self._justify(str(subsection), self.render_anchor(subsection.anchor))
        return self._multiline(l1, "-"*len(subsection))



    def render_list(self, report_list):
        ls = []
        if report_list.headline is not None:
            ls.append(self.dispatch(report_list.headline))

        for li in report_list:
            with increment_width(self, -3):
                li_str = self.dispatch(li)
            ls.append(" - {}".format(li_str))

        return self._multiline(*ls)


    def render_description(self, description):
        ls = []
        if description.headline is not None:
            ls.append(self.dispatch(description.headline))

        for k, v in description:
            with increment_width(self, -3):
                k_str = self.dispatch(k)
                with increment_width(self, -(len(k_str)+1)):
                    v_str = self.dispatch(v)

            ls.append(" - {}:{}".format(k_str, v_str))


        return self._multiline(*ls)


    def render_table(self, table):
        # Content
        column_widths = [0] * table.n_cols

        def to_content(row):
            return [self.dispatch(x) for x in row]

        def update_widths(row):
            for i, cell in enumerate(row):
                if len(cell) > column_widths[i]:
                    column_widths[i] = len(cell)

        def both(row):
            if row is None:
                return None
            new_row = to_content(row)
            update_widths(new_row)
            return new_row

        header = both(table.header)
        content = []
        for row in table:
            content.append(both(row))
        footer = both(table.footer)


        # Format
        lines = []
        column_widths = [x+2 for x in column_widths]
        def row2str(row):
            s = ""
            for w, c in zip(column_widths, row):
                s += ("| " + c.ljust(w-1))
            return s + "|"

        hline = ""
        for width in column_widths:
            hline += ("+" + "-"*width)
        hline += "+"

        lines.append(hline)
        if header:
            lines.append(row2str(header))
            lines.append(hline)
        for row in content:
            lines.append(row2str(row))
        lines.append(hline)
        if footer:
            lines.append(row2str(footer))
            lines.append(hline)
        return self._multiline(*lines)


    def render_snippet(self, snippet):
        # TODO use pygments for syntax-coloring
        lines = []
        if snippet.desc is not None:
            lines.append(snippet.desc)
        for n, line in snippet:
            lines.append("{:4}:{}".format(n, line))
        lines.append("")
        return self._multiline(*lines)

