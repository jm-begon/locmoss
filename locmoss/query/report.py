class Header(str):
    pass

class Raw(str):
    pass

class ReportList(object):
    def __init__(self, headline=None):
        self.headline = headline
        self.content = []

    def append(self, o):
        self.content.append(o)

    def extend(self, it):
        for x in it:
            self.append(x)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __iter__(self):
        return iter(self.content)


class Table(object):
    def __init__(self, n_cols, header=None, footer=None):
        self.header = header
        self.rows = []
        self.footer = footer
        self.n_cols = n_cols

        self.column_widths = [0]*n_cols

        if header is not None:
            self._adjust_width(header)

        if footer is not None:
            self._adjust_width(footer)

    def _adjust_width(self, row):
        for i, s in enumerate(row):
            if len(s) > self.column_widths[i]:
                self.column_widths[i] = len(s)


    def append(self, *cell_contents):
        self.rows.append(cell_contents)
        self._adjust_width(cell_contents)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __iter__(self):
        return iter(self.rows)




class Report(object):
    def __init__(self):
        self.content = []

    def __iter__(self):
        return iter(self.content)

    def add_header(self, s):
        self.content.append(Header(s))

    def add_raw(self, *l):
        self.content.append(Raw(" ".join(str(x) for x in l)))
        return self

    def add_list(self, headline=None):
        ls = ReportList(headline)
        self.content.append(ls)
        return ls

    def add_table(self, n_cols, header=None, footer=None):
        table = Table(n_cols, header, footer)
        self.content.append(table)
        return table

    def merge(self, other):
        self.content.extend(other.content)


