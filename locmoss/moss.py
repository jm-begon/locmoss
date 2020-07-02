from collections import defaultdict

from locmoss.query import TerminalRenderer

from locmoss.match import MatchingGraph
from locmoss.query.report import Report


class InvertIndex(object):
    """
    `InvertIndex`
    =============
    Mapping fingerprints to softwares.

    Content is not supposed to be directly altered (use `add` and `invalidate`)
    """
    def __init__(self):
        self.hash_t = defaultdict(set)
        self.skips = set()
        self._matching_graph = None
        self._softwares = None

    def _dirty(self):
        self._matching_graph = None
        self._softwares = None

    def add(self, fingerprint, software, skip=False):
        self._dirty()
        if skip:
            self.skips.add(fingerprint)
        if fingerprint not in self.skips:
            self.hash_t[fingerprint].add(software)

    def invalidate(self, fingerprint):
        self._dirty()
        self.skips.add(fingerprint)

    def __getitem__(self, fingerprint):
        if fingerprint in self.skips:
            return frozenset()
        return self.hash_t[fingerprint]

    def __iter__(self):
        for fp, sw in self.hash_t.items():
            if fp not in self.skips:
                yield fp, sw

    def iter_raw(self):
        for fp, sw in self.hash_t.items():
            yield fp, sw

    def is_skipped(self, fingerprint):
        return fingerprint in self.skips


    def get_softwares(self):
        if self._softwares is None:
            all_soft = set()
            for softwares in self.hash_t.values():
                all_soft.update(softwares)
            self._softwares = all_soft
        return self._softwares


    def derive_matching_graph(self):
        if self._matching_graph is None:
            self._matching_graph = MatchingGraph.from_invert_index(self)
        return self._matching_graph


class Filter(object):
    def __init__(self, collision_threshold):
        self.collision_threshold = collision_threshold

    def __call__(self, invert_index):
        for fp, s in invert_index:
            if len(s) > self.collision_threshold:
                invert_index.invalidate(fp)




class MossEngine(object):
    """
    Start by adding the reference file
    """
    def __init__(self, fingerprinter, filter=None, renderer=None):
        self.fingerprinter = fingerprinter
        if filter is None:
            filter = lambda x: x
        self.filter = filter
        if renderer is None:
            renderer = TerminalRenderer()
        self.renderer = renderer
        self.invert_index = InvertIndex()

    def fingerprint(self, software):
        for location, fingerprint in self.fingerprinter.extract_fingerprints(software):
            software.add_fingerprint(fingerprint, location)


    def update_index(self, software, reference=False):
        for fp in software.fingerprints:
            self.invert_index.add(fp, software, skip=reference)



    def build_index(self, softwares, reference_software=None):
        if reference_software is not None:
            self.fingerprint(reference_software)
            self.update_index(reference_software, True)
        for software in softwares:
            self.fingerprint(software)
            self.update_index(software)
        self.filter(self.invert_index)
        return self


    def query(self, a_query):
        result = a_query(self.invert_index)
        if isinstance(result, Report):
            self.renderer(result)
        return result












