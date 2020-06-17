from collections import defaultdict

class InvertIndex(object):
    def __init__(self):
        self.hash_t = defaultdict(set)
        self.skips = set()

    def add(self, fingerprint, software, skip=False):
        if skip:
            self.skips.add(fingerprint)
        if fingerprint not in self.skips:
            self.hash_t[fingerprint].add(software)


class Moss(object):
    """
    Start by adding the reference file
    """
    def __init__(self, fingerprinter):
        self.fingerprinter = fingerprinter
        self.invert_index = InvertIndex()

    def fingerprint(self, software):
        for location, fingerprint in self.fingerprinter.extract_fingerprints(software):
            software.add_fingerprint(fingerprint, location)

    def update_index(self, software, reference=False):
        for fp in software.fingerprints:
            self.invert_index.add(fp, software, skip=reference)


    def build_index(self, softwares, reference_software):
        self.update_index(reference_software, True)
        for software in softwares:
            self.fingerprint(software)
            self.update_index(software)









