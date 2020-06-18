from collections import defaultdict


class MatchingGraph(object):
    def __init__(self):
        self.i2s = []
        self.n2i = {}
        self.shareprints = defaultdict(set)

    def _idx(self, int_or_software):
        try:
            return int(int_or_software)
        except TypeError:
            software = int_or_software
            idx = self.n2i.get(software.name)
            if idx is None:
                idx = len(self.i2s)
                self.n2i[software.name] = idx
                self.i2s.append(software)
            return idx


    def add_match(self, s1, s2, fingerprint):
        idx1 = self._idx(s1)
        idx2 = self._idx(s2)
        idx_a, idx_b = (idx1, idx2) if idx1 < idx2 else (idx2, idx1)

        self.shareprints[(idx_a, idx_b)].add(fingerprint)

    def software_from_name(self, name):
        return self.i2s[self.n2i[name]]

    def __iter__(self):
        for (idx1, idx2), fingerprint in self.shareprints.items():
            yield self.i2s[idx1], self.i2s[idx2], fingerprint

    def __getitem__(self, item):
        idx1, idx2 = item
        idx1, idx2 = self._idx(idx1), self._idx(idx2)

        idx_a, idx_b = (idx1, idx2) if idx1 < idx2 else (idx2, idx1)

        return self.shareprints.get((idx_a, idx_b))

    def __len__(self):
        return len(self.shareprints)


