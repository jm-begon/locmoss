from locmoss.query.report import Report
from .scorer import CountScorer


class Query(object):
    def __init__(self, label=None):
        self.label = self.__class__.__name__ if label is None else label

    def query_(self, report, invert_index):
        pass

    def __call__(self, invert_index):
        report = Report()
        report.add_header(self.label)
        self.query_(report, invert_index)
        return report


class SoftwareList(Query):
    def query_(self, report, invert_index):
        softwares = invert_index.get_softwares()
        for sf in softwares:
            with report.add_list(sf.name) as report_list:
                report_list.extend(sf)


class CorpusStat(Query):
    def query_(self, report, invert_index):
        n_fp = 0
        n_skipped = 0
        n_collisions = 0
        for fingerprint, softwares in invert_index.iter_raw():
            n_fp += 1
            if invert_index.is_skipped(fingerprint):
                n_skipped += 1
            else:
                if len(softwares) > 1:
                    n_collisions += 1


        n_softwares = len(invert_index.get_softwares())
        with report.add_list() as report_list:
            report_list.append("Number of softwares: {}".format(n_softwares))
            report_list.append("Total number of fingerprints: {}".format(n_fp))
            report_list.append("Number of active fingerprints: {}"
                               "".format(n_fp - n_skipped))
            report_list.append("Number of collisions: {}".format(n_collisions))




class Ranking(Query):
    class AllScores(object):
        def __init__(self, software_1, software_2, scores):
            self.software_1 = software_1
            self.software_2 = software_2
            self.scores = scores


        def __iter__(self):
            for score in self.scores:
                yield score


    def __init__(self, max_size=None, *scorers, label=None):
        # Ordering follow the scorers[0]
        super().__init__(label)
        if len(scorers) == 0:
            scorers = (CountScorer(),)
        self.scorers = scorers
        self.max_size = max_size
        self.ranking = ()


    def query_(self, report, invert_index):
        report.add_raw("First {} results".format(self.max_size))
        def sort_(t):
            software1, software2, shareprints = t
            return self.scorers[0](invert_index, software1, software2, shareprints)

        matching_graph = invert_index.derive_matching_graph()

        ls = []
        for software_1, software_2, shareprints in matching_graph:
            scores =  tuple(scorer(invert_index, software_1, software_2, shareprints)
                     for scorer in self.scorers)
            ls.append(self.__class__.AllScores(software_1, software_2, scores))


        ls.sort(key=lambda x:x.scores,
                reverse=self.scorers[0].higher_more_similar)

        ls = ls[:self.max_size]
        self.ranking = [(m.software_1, m.software_2) for m in ls]

        header = ["Software 1", "Software 2"] + [s.label for s in self.scorers]
        
        with report.add_table(len(header), header) as table:
            for all_scores in ls:
                row = [all_scores.software_1.name,
                       all_scores.software_2.name]
                for scorer, score in zip(self.scorers, all_scores):
                    row.append(scorer.format_str.format(score))
                table.append(*row)

    def __iter__(self):
        iter(self.ranking)


