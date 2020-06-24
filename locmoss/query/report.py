from hashlib import sha1

from collections import OrderedDict

class Raw(str):
    pass

class Newline(object):
    pass

class Anchor(object):
    def __init__(self, s, prefix=None):
        self.s = s
        self.prefix = prefix

    def __str__(self):
        return self.s

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__,
                                   self.s,
                                   self.prefix)

    def as_hash_str(self):
        return "{}{}".format(self.prefix if self.prefix is not None else "",
                             sha1(self.s.encode("utf-8")).hexdigest())



class Anchorable(object):
    @classmethod
    def get_prefix(cls):
        return None

    @classmethod
    def create_anchor(cls, s, anchor=None):
        if anchor is None:
            anchor = Anchor(s, prefix=cls.get_prefix())
        return anchor

    def __init__(self, s, anchor=None):
        self.s = s
        self.anchor = self.__class__.create_anchor(self.s, anchor)

    def __str__(self):
        return self.s

    def __len__(self):
        return len(self.s)

class Header(Anchorable):
    pass


class Section(Anchorable):
    @classmethod
    def get_prefix(cls):
        return "sec:"


class SubSection(Anchorable):
    @classmethod
    def get_prefix(cls):
        return "ssec:"



class Reference(object):
    @classmethod
    def join(cls, *ss):
        return "_".join(ss)


    def __init__(self, s, anchor):
        self.s = s
        self.anchor = anchor if isinstance(anchor, Anchor) else Anchor(anchor)

    def __str__(self):
        return self.s



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


class Description(object):
    def __init__(self, headline=None):
        self.headline = headline
        self.content = OrderedDict()

    def append(self, k, v):
        self.content[k] = v

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __iter__(self):
        for k, v in self.content.items():
            yield k, v


class Table(object):
    def __init__(self, n_cols, header=None, footer=None):
        self.header = header
        self.rows = []
        self.footer = footer
        self.n_cols = n_cols


    def append(self, *cell_contents):
        self.rows.append(cell_contents)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __iter__(self):
        return iter(self.rows)



class Snippet(object):
    def __init__(self, desc=None):
        self.desc = desc
        self.lines = []

    def append(self, line_nb, line):
        self.lines.append((line_nb, line))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __iter__(self):
        for line_nb, line in self.lines:
            yield line_nb, line




class Report(object):
    def __init__(self):
        self.content = []

    def __iter__(self):
        return iter(self.content)

    def add(self, x):
        self.content.append(x)

    def add_newline(self):
        self.add(Newline())

    def add_raw(self, *l):
        self.add(Raw(" ".join(str(x) for x in l)))
        return self

    def add_reference(self, readable_str, anchor_label, prefix=None):
        self.add(Reference(readable_str, Anchor(anchor_label, prefix)))

    def add_header(self, s):
        self.add(Header(s))

    def add_section(self, s):
        self.add(Section(s))

    def add_subsection(self, s):
        self.add(SubSection(s))

    def add_list(self, headline=None):
        ls = ReportList(headline)
        self.add(ls)
        return ls

    def add_description(self, headline=None):
        desc = Description(headline)
        self.add(desc)
        return desc

    def add_table(self, n_cols, header=None, footer=None):
        table = Table(n_cols, header, footer)
        self.add(table)
        return table

    def add_snippet(self, desc=None):
        snippet = Snippet(desc)
        self.add(snippet)
        return snippet

    def merge(self, other):
        self.content.extend(other.content)

