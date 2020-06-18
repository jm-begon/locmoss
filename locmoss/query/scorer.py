from abc import ABCMeta, abstractmethod


class Scorer(object, metaclass=ABCMeta):
    @property
    def label(self):
        return self.__class__.__name__


    @property
    def format_str(self):
        return "{}"


    @property
    def higher_more_similar(self):
        return True


    @abstractmethod
    def __call__(self, invert_index, software_1, software_2, shareprints):
        return 0.0


class CountScorer(Scorer):
    @property
    def label(self):
        return "Number of shareprints"


    def __call__(self, invert_index, software_1, software_2, shareprints):
        return len(shareprints)


class JaccardScorer(Scorer):
    @property
    def label(self):
        return "Jaccard index"

    @property
    def format_str(self):
        return "{:.2}"


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

