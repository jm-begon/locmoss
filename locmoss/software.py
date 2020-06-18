import glob
import os
from collections import OrderedDict
from collections import defaultdict


class Software(object):
    @classmethod
    def list_from_globs(cls, patterns, realpath=False):
        tree = Tree.from_glob_pattern(patterns, realpath)
        return list(tree.to_software())

    def __init__(self, name, files=()):
        self.name = name
        self.source_files = tuple(files)
        self.fingerprints = defaultdict(list)

    def __iter__(self):
        for source_file in self.source_files:
            yield source_file

    def add_fingerprint(self, fingerprint, location):
        self.fingerprints[fingerprint].append(location)

    def yield_fingerprints(self):
        for fp in self.fingerprints.keys():
            yield fp

    def __getitem__(self, fingerprint):
        return self.fingerprints[fingerprint]

    def count_fingerprints(self):
        return len(self.fingerprints)

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__,
                                   repr(self.name),
                                   repr({x for x in self}))



class Tree(object):
    @classmethod
    def from_glob_pattern(cls, patterns, realpath=False):
        tree = cls()
        for pattern in patterns:
            for file in glob.glob(pattern):
                path = os.path.expanduser(file)
                if realpath:
                    path = os.path.realpath(path)
                splits = path.split(os.sep)
                if len(splits[0]) == 0:
                    tup = (os.sep,) + tuple(splits[1:])
                else:
                    tup = tuple(splits)
                tree.insert(tup)
        return tree


    def __init__(self):
        self.children = OrderedDict()

    def insert(self, tup):
        if len(tup) == 0:
            return
        head, tail = tup[0], tup[1:]

        child = self.children.get(head)
        if child is None:
            child = Tree()
            self.children[head] = child

        child.insert(tail)

    def to_software(self):
        common = []
        children = self.children
        while len(children) < 2:
            if len(children) == 0:
                raise ValueError("No software found.")
            label, subtree = list(children.items())[0]
            common.append(label)
            children = subtree.children

        prefix = os.sep.join(common)
        for software_name, subtree in children.items():
            software_path = os.path.join(prefix, software_name)
            files = []
            for source_sub_path in subtree:
                source_path = os.path.join(software_path, source_sub_path)
                files.append(source_path)

            software = Software(software_path, files)
            yield software


    def __iter__(self):
        for label, child in self.children.items():
            if len(child.children) == 0:
                yield label
            else:
                for x in child:
                    yield os.path.join(label, x)




