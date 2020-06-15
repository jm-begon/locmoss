from .struct import KGrams

class Winnower(object):
    def __init__(self, window_size, k, hash_fn=None):
        self.window_size = window_size
        self.k = k
        self.hash_fn = hash_fn

    def compute_fingerprints(self, tokens):
        kgrams = KGrams.kgramify(tokens, self.k, self.hash_fn)
        raw_fingerprints = []
        # TODO
        return raw_fingerprints
