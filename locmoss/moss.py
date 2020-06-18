from collections import defaultdict

from locmoss.match import MatchingGraph


class InvertIndex(object):
    """
    `InvertIndex`
    =============
    Mapping fingerprints to softwares
    """
    def __init__(self):
        self.hash_t = defaultdict(set)
        self.skips = set()

    def add(self, fingerprint, software, skip=False):
        if skip:
            self.skips.add(fingerprint)
        if fingerprint not in self.skips:
            self.hash_t[fingerprint].add(software)

    def invalidate(self, fingerprint):
        self.skips.add(fingerprint)

    def __getitem__(self, fingerprint):
        if fingerprint in self.skips:
            return frozenset()
        return self.hash_t[fingerprint]

    def __iter__(self):
        for fp, sw in self.hash_t.items():
            if fp not in self.skips:
                yield fp, sw

    def get_softwares(self):
        all_soft = set()
        for softwares in self.hash_t.values():
            all_soft.update(softwares)
        return all_soft


class Filter(object):
    def __init__(self, collision_threshold):
        self.collision_threshold = collision_threshold

    def __call__(self, invert_index):
        for fp, s in invert_index:
            if len(s) > self.collision_threshold:
                invert_index.invalidate(fp)




class Moss(object):
    """
    Start by adding the reference file
    """
    def __init__(self, fingerprinter, filter=None):
        self.fingerprinter = fingerprinter
        if filter is None:
            filter = lambda x: x
        self.filter = filter
        self.invert_index = InvertIndex()

    def fingerprint(self, software):
        for location, fingerprint in self.fingerprinter.extract_fingerprints(software):
            software.add_fingerprint(fingerprint, location)

    def update_index(self, software, reference=False):
        for fp in software.fingerprints:
            self.invert_index.add(fp, software, skip=reference)


    def build_index(self, softwares, reference_software=None):
        if reference_software is not None:
            self.update_index(reference_software, True)
        for software in softwares:
            self.fingerprint(software)
            self.update_index(software)
        self.filter(self.invert_index)
        return self

    def build_matching_graph(self):
        softwares = self.invert_index.get_softwares()
        graph = MatchingGraph()
        for s1 in softwares:
            for fingerprint in s1.yield_fingerprints():
                matching_software = self.invert_index[fingerprint]
                for s2 in matching_software:
                    if s1.name < s2.name:
                        # No need to count self matches
                        # and symetry is taken care of by the graph
                        graph.add_match(s1, s2, fingerprint)

        return graph











