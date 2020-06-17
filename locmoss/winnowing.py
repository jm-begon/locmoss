from .fingerprint import Fingerprinter
from .kgram import KGrams, Buffer



class Winnower(Fingerprinter):
    def __init__(self, parser_factory, window_size, k):
        super().__init__(parser_factory)
        self.window_size = window_size
        self.k = k

    @property
    def kgramifier(self):
        # Can be overriden to change the default hash function
        return KGrams.kgramify


    def extract_fingerprints_(self, token_iterator):
        window = Buffer(self.window_size)
        selected_grams = []
        min_gram = None

        for location, kgram in self.kgramifier(token_iterator, self.k):
            window.put(kgram)
            if window.is_full():
                # Note: using built-in `min` should be much faster than
                # re-impl. it. Moreover, the window is expected to be small
                # and the cost of deriving and inverting an array should be
                # small.
                # `min` keeps the leftmost minima:
                # >> min([(1, 1), (1, 2)], key=lambda x:x[0])
                # (1, 1)
                window_min = min(list(window)[::-1], key=hash)
                if window_min is not min_gram:
                    selected_grams.append(window_min)
                    min_gram = window_min
                    yield location, window_min


