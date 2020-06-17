import os

import pygments.token
import pygments.lexers

from locmoss.location import Location



class Token(object):
    def __init__(self, symbol, location):
        self.symbol = symbol
        self.location = location

    def __str__(self):
        return str(self.symbol)

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__,
                                       repr(self.symbol),
                                       repr(self.location))

class Parser(object):
    def __init__(self, fpath, lexer=None, encoding="latin-1"):
        self.fpath = fpath
        self.lexer = lexer
        self.encoding = encoding


    def __repr__(self):
        return "{}({}, {}, {})".format(self.__class__.__name__,
                                       repr(self.fpath),
                                       repr(self.lexer),
                                       repr(self.encoding))

    def __iter__(self):
        with open(self.fpath, "r", encoding=self.encoding) as hdl:
            text = hdl.read()
        lexer = pygments.lexers.guess_lexer_for_filename(self.fpath, text) \
            if self.lexer is None else self.lexer

        # Adapted from https://github.com/agranya99/MOSS-winnowing-seqMatcher/blob/master/cleanUP.py
        for j, line in enumerate(text.split(os.linesep)):
            line_number = j + 1
            column_number = 0
            for token_type, symbol in lexer.get_tokens(line):
                if token_type == pygments.token.Text or token_type in pygments.token.Comment:
                    symbol = None
                elif token_type == pygments.token.Name:
                    symbol = "N"  # all variable names as 'N'
                elif token_type in pygments.token.Literal.String:
                    symbol = "S"  # all strings as 'S'
                elif token_type in pygments.token.Name.Function:
                    symbol = "F"  # user defined function names as 'F'


                if symbol is not None:
                    yield Token(symbol, Location(self.fpath, line_number,
                                                 column_number))

                column_number += len(symbol)


