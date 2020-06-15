
from hashlib import sha1

class Token(object):
    def __init__(self, symbol, original_position, noisefree_position):
        self.symbol = symbol
        self.original_position = original_position
        self.noisefree_position = noisefree_position

    def __str__(self):
        return str(self.symbol)

    def __repr__(self):
        return "{}({}, {}, {})".format(self.__class__.__name__,
                                       repr(self.symbol),
                                       repr(self.original_position),
                                       repr(self.noisefree_position))


class KGrams(object):
    @classmethod
    def default_hash_fn(cls, tokens):
        s = ''.join(token.symbol for token in tokens)
        hashval = sha1(s)
        hashval = hashval.hexdigest()[-4:]
        hashval = int(hashval, 16)  # using last 16 bits of sha-1 digest
        return hashval

    @classmethod
    def kgramify(cls, tokens, k=5, hash_fn=None):
        kgrams = []
        n = len(tokens)
        for i in range(n - k + 1):
            kgrams.append(cls(*[tokens[i:i + k]], hash_fn=hash_fn))

        return kgrams

    def __init__(self, *tokens, hash_fn=None):
        self.tokens = tokens
        self.hash_fn = hash_fn
        if self.hash_fn is None:
            self.hash_val = self.__class__.default_hash_fn(self.tokens)
        else:
            self.hash_val = self.hash_fn(self.tokens)


    @property
    def original_start(self):
        return self.tokens[0].original_position

    @property
    def original_end(self):
        return self.tokens[-1].original_position

    @property
    def noisefree_start(self):
        return self.tokens[0].noisefree_position

    @property
    def noisefree_end(self):
        return self.tokens[-1].noisefree_position

    def __len__(self):
        return len(self.tokens)

    def __hash__(self):
        return self.hash_val

    def __eq__(self, other):
        if not isinstance(other, KGrams) or not len(self) == len(other):
            return False

        for s_tok, o_tok in zip(self.tokens, other.tokens):
            if s_tok != o_tok:
                return False
        return True

    def __str__(self):
        return "".join(str(token) for token in self.tokens)


class SourceFile(object):
    def __init__(self, fpath, original_length, noisefree_length):
        self.fpath = fpath
        self.original_length = original_length
        self.noisefree_length = noisefree_length
        self.software = None
        self.fingerprints = []

    def attach_to_software(self, software):
        self.software = software
        software.add(self)
        return self

    def attach_fingerprint(self, fingerprint):
        self.fingerprints.append(fingerprint)
        return self

    def count_fingerprints(self):
        return len(self.fingerprints)


class Software(set):
    def __init__(self, name, seq=()):
        super().__init__(seq)
        self.name = name

    def original_length(self):
        return sum(sf.original_length for sf in self)

    def noisefree_length(self):
        return sum(sf.noisefree_length for sf in self)

    def count_fingerprints(self):
        return sum(sf.count_fingerprints() for sf in self)


class Fingerprint(object):
    def __init__(self, source_file, kgram):
        self.source_file = source_file.attch_fingerprint(self)
        self.kgram = kgram

    @property
    def skip(self):
        return False

    @property
    def software(self):
        return self.source_file.software

    def __hash__(self):
        return hash(self.kgram)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.kgram == other.kgram

    def is_collision(self, other):
        return other is not None and \
               not self.skip and \
               not other.skip and  \
               other.software == self.software


class Skipper(Fingerprint):
    @property
    def skip(self):
        return True


