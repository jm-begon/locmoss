import pygments.token
import pygments.lexers

from .struct import Token, SourceFile

class Parser(object):
    def __init__(self, fpath, lexer=None, encoding="latin-1"):
        self.fpath = fpath
        self.lexer = lexer
        self.encoding = encoding
        self.original_length = None
        self.noisefree_length = None

    @property
    def source_file(self):
        if self.original_length is None or self.noisefree_length is None:
            raise ValueError("Iter first to get the lengths.")
        return SourceFile(self.fpath, self.original_length,
                          self.noisefree_length)


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

        # from https://github.com/agranya99/MOSS-winnowing-seqMatcher/blob/master/cleanUP.py
        tokens = lexer.get_tokens(text)
        tokens = list(tokens)
        lenT = len(tokens)
        count1 = 0  # tag to store corresponding position of each element in original code file
        count2 = 0  # tag to store position of each element in cleaned up code text
        # these tags are used to mark the plagiarized content in the original code files.
        for i in range(lenT):
            if tokens[i][0] == pygments.token.Text or tokens[i][0] in pygments.token.Comment:
                symbol = None
                inc2 = 0
            elif tokens[i][0] == pygments.token.Name and not i == lenT - 1 and not tokens[i + 1][1] == '(':
                symbol = "N"  # all variable names as 'N'
                inc2 = 1
            elif tokens[i][0] in pygments.token.Literal.String:
                symbol = "S"  # all strings as 'S'
                inc2 = 1
            elif tokens[i][0] in pygments.token.Name.Function:
                symbol = "F"  # user defined function names as 'F'
                inc2 = 1
            else:
                symbol = tokens[i][1]
                inc2 = len(tokens[i][1])

            if symbol is not None:
                yield Token(symbol, count1, count2)
            count1 += len(tokens[i][1])
            count2 += inc2

        self.original_length = count1
        self.noisefree_length = count2

