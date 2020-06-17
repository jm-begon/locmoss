
from hashlib import sha1


class Buffer(object):
    def __init__(self, capacity):
        self.circ = [None for _ in range(capacity)]
        self.top = 0

    def __iter__(self):
        size = len(self.circ)
        for i in range(size):
            o = self.circ[(self.top + i) % size]
            if o is None:
                raise StopIteration()
            yield o

    def put(self, o):
        self.circ[self.top % len(self.circ)] = o
        self.top += 1

    def is_full(self):
        return self.top >= len(self.circ)


class KGrams(object):
    @classmethod
    def default_hash_fn(cls, tokens):
        s = ''.join(token.symbol for token in tokens)
        hashval = sha1(s.encode("utf-8"))
        hashval = hashval.hexdigest()[-4:]
        hashval = int(hashval, 16)  # using last 16 bits of sha-1 digest
        return hashval

    @classmethod
    def kgramify(cls, token_iterator, k=5):
        buffer = Buffer(k)
        for token in token_iterator:
            buffer.put(token)
            if buffer.is_full():
                symbols = list(buffer)
                yield symbols[0].location, cls(symbols)

    def __init__(self, symbols):
        self.symbols = tuple(symbols)
        self.hash_val = self.__class__.default_hash_fn(self.symbols)

    def __len__(self):
        return len(self.symbols)

    def __hash__(self):
        return self.hash_val

    def __eq__(self, other):
        if not isinstance(other, KGrams) or not len(self) == len(other):
            return False

        for s_tok, o_tok in zip(self.symbols, other.tokens):
            if s_tok.symbol != o_tok.symbol:
                return False
        return True

    def __str__(self):
        return "".join(str(token) for token in self.symbols)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__,
                               repr(self.symbols))
