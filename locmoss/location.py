
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


