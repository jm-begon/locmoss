from collections import defaultdict

from .struct import Fingerprint, Skipper, Software
from .winnowing import Winnower
from .match import MatchingGraph


class Moss(object):
    """
    Start by adding the reference file
    """
    def __init__(self, parser_factory):
        self.parser_factory = parser_factory
        self.collison_table = defaultdict(list)
        self.matchings = MatchingGraph()

    @property
    def matching_graph(self):
        return self.matchings

    def _insert(self, fingerprint):
        ls = self.collison_table.get(fingerprint)
        # Search for collision
        if ls is not None:
            if ls[0].skip:
                # No need to store anything
                return
            for fp in ls:
                if fingerprint.is_collision(fp):
                    self.matchings.add_match(fingerprint, fp)


        self.collison_table[fingerprint].append(fingerprint)

    def update_index(self, software_name, software_files, reference=False):
        fp_factory = Skipper if reference else Fingerprint
        software = Software(software_name)

        for i, fpath in enumerate(software_files):
            winnower = Winnower()
            parser = self.parser_factory(fpath)
            raw_fingerprints = winnower.compute_fingerprints(parser)
            source_file = parser.source_file.attach_to_software(software)

            for raw_fp in raw_fingerprints:
                fingerprint = fp_factory(source_file, fpath, raw_fp)
                self._insert(fingerprint)





