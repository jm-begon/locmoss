
class Location(object):
    def __init__(self, source_file, start_line, start_column):
        self.source_file = source_file
        self.start_line = start_line
        self.start_column = start_column

    def __str__(self):
        return "{}:{}:{}".format(self.source_file, self.start_line, self.start_column)

    def __repr__(self):
        return "{}({}, {}, {})".format(self.__class__.__name__,
                                       repr(self.source_file),
                                       repr(self.start_line),
                                       repr(self.start_column))


class LocationIterator(object):
    def __init__(self, pre_lines=0, post_lines=0, encoding="latin-1"):
        self.pre_lines = pre_lines
        self.post_lines = post_lines
        self.encoding = encoding


    def __call__(self, location):
        # TODO do something more efficient
        pre = max(1, location.start_line - self.pre_lines)
        post = location.start_line + self.post_lines
        with open(location.source_file, "r", encoding=self.encoding) as hdl:
            for i, line in enumerate(hdl):
                line_nb = i + 1
                if line_nb > post:
                    break
                if pre < line_nb:
                    yield line_nb, line.rstrip()