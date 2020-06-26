from abc import ABCMeta, abstractmethod

import math


class Scorer(object, metaclass=ABCMeta):
    @property
    def label(self):
        return self.__class__.__name__


    def format_score(self, x):
        return str(x)


    @property
    def higher_more_similar(self):
        return True


    @abstractmethod
    def __call__(self, invert_index, software_1, software_2, shareprints):
        return 0.0


class CountScorer(Scorer):
    @property
    def label(self):
        return "# Shareprints"


    def __call__(self, invert_index, software_1, software_2, shareprints):
        return len(shareprints)


class JaccardScorer(Scorer):
    @property
    def label(self):
        return "Jaccard index"

    def format_score(self, x):
        return "{:.2f}".format(x).zfill(2)

    def _count_active_fingerprints(self, invert_index, software):
        n = software.count_fingerprints()
        for fp in software.yield_fingerprints():
            if invert_index.is_skipped(fp):
                n -= 1
        return n

    def __call__(self, invert_index, software_1, software_2, shareprints):
        n_fp1 = self._count_active_fingerprints(invert_index, software_1)
        n_fp2 = self._count_active_fingerprints(invert_index, software_2)

        return float(len(shareprints)) / (n_fp1 + n_fp2 - len(shareprints))


class TfIdfScorer(Scorer):
    def __init__(self):
        self.tf_cache = {}
        self.idf_cache = {}
        self.norm_cache = {}

    @property
    def label(self):
        return "Cos Tf-Idf"

    def format_score(self, x):
        return "{:.2f}".format(x).zfill(2)


    def _tf(self, invert_index, fingerprint, software):
        # Augmented Frequency (aka. double normalization 0.5) is used
        # to treat all softwares similarly, independently of the number
        # of fingerprints they contain

        max_n_fp = max(len(software[fp])
                       for fp in software.yield_fingerprints()
                       if not invert_index.is_skipped(fp))

        return .5 + .5 * len(software[fingerprint]) / float(max_n_fp)

    def _idf(self, fingerprint, invert_index):
        n_softwares = len(invert_index.get_softwares())
        n_softwares_with_fp = len(invert_index[fingerprint])
        return math.log(n_softwares / float(n_softwares_with_fp))

    def tfidf(self, invert_index, fingerprint, software):
        tf = self.tf_cache.get((fingerprint, software))
        if tf is None:
            tf = self._tf(invert_index, fingerprint, software)
            self.tf_cache[(fingerprint, software)] = tf

        idf = self.idf_cache.get(fingerprint)
        if idf is None:
            idf = self._idf(fingerprint, invert_index)
            self.idf_cache[fingerprint] = idf

        return tf * idf

    def norm(self, invert_index, software):
        x = self.norm_cache.get(software)
        if x is None:
            x = math.sqrt(sum(self.tfidf(invert_index, fingerprint, software)**2
                             for fingerprint in software.yield_fingerprints()
                              if not invert_index.is_skipped(fingerprint)))
            self.norm_cache[software] = x
        return x

    def __call__(self, invert_index, software_1, software_2, shareprints):
        # Cosine similarity
        sp = sum((self.tfidf(invert_index, fingerprint, software_1) *
                  self.tfidf(invert_index, fingerprint, software_1))
                 for fingerprint in shareprints
                 if not invert_index.is_skipped(fingerprint))

        n_1 = self.norm(invert_index, software_1)
        n_2 = self.norm(invert_index, software_2)

        return sp / (n_1 * n_2)
