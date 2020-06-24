import os

from datetime import datetime, timedelta

from locmoss.location import LocationIterator
from locmoss.query.report import Report, Anchor, Anchorable, Reference, \
    SubSection, Section
from .scorer import CountScorer


class Query(object):
    def __init__(self, label=None):
        self.label = self.__class__.__name__ if label is None else label


    def header(self, report):
        report.add_header(self.label)


    def query_(self, report, invert_index):
        pass

    def __call__(self, invert_index):
        report = Report()
        self.header(report)
        self.query_(report, invert_index)
        return report

class MetaData(Query):
    __HEADER__ = """   __                 _             ___  __  __     __                       _
  / /  ___   ___ __ _| |   /\/\    /___\/ _\/ _\   /__\ ___ _ __   ___  _ __| |_
 / /  / _ \ / __/ _` | |  /    \  //  //\ \ \ \   / \/// _ \ '_ \ / _ \| '__| __|
/ /__| (_) | (_| (_| | | / /\/\ \/ \_// _\ \_\ \ / _  \  __/ |_) | (_) | |  | |_
\____/\___/ \___\__,_|_| \/    \/\___/  \__/\__/ \/ \_/\___| .__/ \___/|_|   \__|
                                                           |_|                   """
    def __init__(self, **context):
        super().__init__()
        self.dict = context
        self.creation = datetime.now()

    def duration_str(self, duration_in_sec):
        s = str(duration_in_sec)
        # remove milliseconds and stuff
        return s.split(".")[0]

    def header(self, report):
        for line in self.__HEADER__.split(os.linesep):
            report.add_raw(line)

    def query_(self, report, invert_index):
        now = datetime.now()
        with report.add_list("Context") as ls:
            for k,v in self.dict.items():
                ls.append("{}: {}".format(k, v))

            ls.append("Hash: {}".format(hash(invert_index)))
            ls.append("Duration: {}".format(self.duration_str(now - self.creation)))






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

        header = ["Rank", "Software 1", "Software 2"] + [s.label for s in self.scorers]
        
        with report.add_table(len(header), header) as table:
            # TODO anchor
            for i, all_scores in enumerate(ls):
                s1_name = all_scores.software_1.name
                s2_name = all_scores.software_2.name
                anchor = Section.create_anchor(Reference.join(s1_name, s2_name))

                row = [Reference(str(i+1), anchor), s1_name, s2_name]
                for scorer, score in zip(self.scorers, all_scores):
                    row.append(scorer.format_score(score))
                table.append(*row)

    def __iter__(self):
        return iter(self.ranking)


class MatchingLocations(Query):
    def __init__(self, software_pairs, label=None):
        super().__init__(label)
        self.software_pairs = software_pairs

    def query_(self, report, invert_index):
        matching_graph = invert_index.derive_matching_graph()

        for soft_1, soft_2 in self.software_pairs:
            s1_name, s2_name = soft_1.name, soft_2.name
            anchor = Section.create_anchor(Reference.join(s1_name, s2_name))

            shareprints = matching_graph[(soft_1, soft_2)]
            report.add(Section("{} VS. {}".format(s1_name, s2_name), anchor))
            report.add_raw("Matching fingerprints: {}".format(len(shareprints)))
            report.add_newline()


            for fingerprint in shareprints:

                with report.add_list(str(fingerprint)) as report_list:
                    for software in (soft_1, soft_2):
                        locations = software[fingerprint]
                        for location in locations:
                            desc = "{}:{}:{}".format(location.source_file,
                                                     location.start_line,
                                                     location.start_column)
                            report_list.append(desc)


                report.add_newline()




class MatchingSnippets(Query):
    def __init__(self, software_pairs, pre_lines=5, post_lines=5,
                 label=None):
        super().__init__(label)
        self.software_pairs = software_pairs
        self.loc_iter = LocationIterator(pre_lines, post_lines)


    def query_(self, report, invert_index):
        matching_graph = invert_index.derive_matching_graph()

        anchors = {}

        for soft_1, soft_2 in self.software_pairs:
            s1_name, s2_name = soft_1.name, soft_2.name
            anchor = Section.create_anchor(Reference.join(s1_name, s2_name))

            report.add(Section("{} VS. {}".format(s1_name, s2_name), anchor))

            shareprints = matching_graph[(soft_1, soft_2)]

            with report.add_list("Matching fingerprints: {}".format(len(shareprints))) as li:
                for fingerprint in shareprints:
                    ref_s = Reference.join(s1_name, s2_name, str(fingerprint))
                    anchor = SubSection.create_anchor(ref_s)

                    anchors[ref_s] = anchor

                    li.append(Reference(str(fingerprint), anchor))


            report.add_newline()

            for fingerprint in shareprints:
                s_fp = str(fingerprint)
                ref_s = Reference.join(s1_name, s2_name, s_fp)
                report.add(SubSection(s_fp, anchors[ref_s]))

                for software in (soft_1, soft_2):
                    locations = software[fingerprint]
                    for location in locations:
                        desc = "{}:{}:{}".format(location.source_file,
                                                 location.start_line,
                                                 location.start_column)
                        with report.add_snippet(desc) as snippet:
                            for ln, line in self.loc_iter(location):
                                snippet.append(ln, line)
