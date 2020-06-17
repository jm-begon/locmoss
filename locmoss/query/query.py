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


class JaccardSorted(Query):
    def __init__(self, threshold=0., max_size=None, label=None, renderer=None):
        super().__init__(label, renderer)
        self.threshold = threshold
        self.max_size = max_size


    def query_(self, matching_graph):
        def sort_by_jaccard(t):
            _, _, common_print = t
            return common_print.jaccard_index()

        ls = sorted(matching_graph, key=sort_by_jaccard, reverse=True)
        for i, (software_name_1, software_name2, match) in enumerate(ls):
            if self.max_size is not None and i > self.max_size:
                break

            jacc_idx = match.jaccard_index()
            if jacc_idx < self.threshold:
                break

            self.renderer.add_raw(("{} - {} - {:.2f}".format(software_name_1,
                                                             software_name2,
                                                             jacc_idx)))




