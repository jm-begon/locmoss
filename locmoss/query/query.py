from .renderer import TerminalRenderer


class Query(object):
    def __init__(self, label=None, renderer=None):
        if renderer is None:
            renderer = TerminalRenderer()
        self.renderer = renderer
        self.label = self.__class__.__name__ if label is None else label

    def query_(self, matching_graph):
        pass

    def __call__(self, matching_graph):
        self.renderer.add_header(self.label)
        self.query_(matching_graph)
        self.renderer.render()

class Sorted(Query):
    def __init__(self, max_size=None, label=None, renderer=None):
        super().__init__(label, renderer)
        self.max_size = max_size

    def query_(self, matching_graph):
        def sort_(t):
            software1, software2, shareprints = t
            return len(shareprints)

        ls = sorted(matching_graph, key=sort_, reverse=True)
        for i, (soft_1, soft_2, match) in enumerate(ls):
            if self.max_size is not None and i > self.max_size:
                break

            self.renderer.add_raw(("{:30} | {:30} | {}".format(soft_1.name,
                                                               soft_2.name,
                                                               len(match))))


class JaccardSorted(Query):
    def __init__(self, threshold=0., max_size=None, label=None, renderer=None):
        super().__init__(label, renderer)
        self.threshold = threshold
        self.max_size = max_size


    def query_(self, matching_graph):
        def jaccard(software1, software2, shareprints):
            return float(len(shareprints)) / (software1.count_fingerprints()
                                              + software2.count_fingerprints()
                                              - len(shareprints))

        def sort_by_jaccard(t):
            software1, software2, shareprints = t
            return jaccard(software1, software2, shareprints)

        ls = sorted(matching_graph, key=sort_by_jaccard, reverse=True)
        for i, (software_1, software_2, match) in enumerate(ls):
            if self.max_size is not None and i > self.max_size:
                break

            jacc_idx = jaccard(software_1, software_2, match)
            if jacc_idx < self.threshold:
                break

            self.renderer.add_raw(("{:30} | {:30} | {:.2f}".format(
                software_1.name,
                software_2.name,
                jacc_idx)))
