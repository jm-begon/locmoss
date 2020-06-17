from collections import defaultdict



class Shareprint(object):
    def __init__(self):
        self.fingerprints_1 = []
        self.fingerprints_2 = []

    @property
    def software_1(self):
        return self.fingerprints_1[0].software

    @property
    def software_2(self):
        return self.fingerprints_2[0].software

    def __len__(self):
        return len(self.fingerprints_1)

    def add_match(self, fp1, fp2):
        if fp1.software.name > fp2.software.name:
            fp1, fp2 = fp2, fp1
        self.fingerprints_1.append(fp1)
        self.fingerprints_2.append(fp2)
        return self

    def jaccard_index(self):
        n1 = self.software_1.count_fingerprints()
        n2 = self.software_2.count_fingerprints()
        n_inter = len(self)
        return float(n_inter) / (n1 + n2 + n_inter)

    def __repr__(self):
        ams = ".add_match".join(repr(x) for x in zip(self.fingerprints_1,
                                                     self.fingerprints_2))
        if len(ams) > 0:
            ams = ".add_match" + ams

        return "{}(){}".format(self.__class__.__name__,
                               ams if len(ams) > 0 else "")




class MatchingGraph(object):
    def __init__(self):
        self.i2n = []
        self.n2i = {}
        self.matches = defaultdict(Shareprint)

    def _idx(self, name):
        idx = self.n2i.get(name)
        if idx is None:
            idx = len(self.i2n)
            self.n2i[name] = idx
            self.i2n.append(name)
        return idx


    def add_match(self, fp1, fp2):
        idx1 = self._idx(fp1.software.name)
        idx2 = self._idx(fp2.software.name)
        idx_a, idx_b = (idx1, idx2) if idx1 < idx2 else (idx2, idx1)

        self.matches[(idx_a, idx_b)].add_match(fp1, fp2)

    def __iter__(self):
        for (idx1, idx2), common_print in self.matches.items():
            yield self.i2n[idx1], self.i2n[idx2], common_print

    def __getitem__(self, item):
        idx1, idx2 = item
        if isinstance(idx1, str):
            idx1 = self.n2i[idx1]

        if isinstance(idx2, str):
            idx2 = self.n2i[idx2]

        idx_a, idx_b = (idx1, idx2) if idx1 < idx2 else (idx2, idx1)

        return self.matches.get((idx_a, idx_b))

    def __len__(self):
        return len(self.matches)


