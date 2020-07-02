from abc import ABCMeta, abstractmethod

import math
from contextlib import contextmanager


class Similarity(object, metaclass=ABCMeta):

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





class Ranking(object):
    class ScoredPair(object):
        def __init__(self, score, software_1, software_2):
            self.score = score
            self.software_1 = software_1
            self.software_2 = software_2

    @classmethod
    def from_invert_index(cls, similarity, invert_index):
        ranking = cls(similarity)


        matching_graph = invert_index.derive_matching_graph()

        ls = []
        for software_1, software_2, shareprints in matching_graph:
            score = similarity(invert_index, software_1, software_2, shareprints)
            ls.append(cls.ScoredPair(score, software_1, software_2))

        ls.sort(key=lambda x: x.score,
                reverse=similarity.higher_more_similar)

        map = {}
        for i, scored_pair in enumerate(ls):
            map[(scored_pair.software_1, scored_pair.software_2)] = i

        ranking.ranking = ls
        ranking.map = map

        return ranking

    @classmethod
    def as_query(cls, similarity):
        def query(invert_index):
            return cls.from_invert_index(similarity, invert_index)
        return query


    def __init__(self, similarity):
        self.similarity = similarity
        self.ranking = None
        self.map = None
        self.max_size = None

    def __iter__(self):
        for i, scored_pair in enumerate(self.ranking):
            if self.max_size is None or i < self.max_size:
                yield scored_pair.score, scored_pair.software_1, \
                      scored_pair.software_2

    def __getitem__(self, item):
        s1, s2 = item
        i = self.map[(s1, s2)]
        return self.ranking[i].score

    def __len__(self):
        return len(self.ranking) if self.max_size is None else self.max_size

    @property
    def label(self):
        return self.similarity.label

    @contextmanager
    def top(self, k):
        max_size = self.max_size
        self.max_size = k
        try:
            yield self
        finally:
            self.max_size = max_size




class CountSimilarity(Similarity):
    @property
    def label(self):
        return "# Shareprints"


    def __call__(self, invert_index, software_1, software_2, shareprints):
        return len(shareprints)


class JaccardSimilarity(Similarity):
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


class TfIdfSimilarity(Similarity):
    def __init__(self):
        self.tf_cache = {}
        self.idf_cache = {}
        self.norm_cache = {}

    @property
    def label(self):
        return "Cosine Tf-Idf"

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
