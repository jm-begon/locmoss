from abc import ABCMeta, abstractmethod


class Fingerprinter(object, metaclass=ABCMeta):

    def __init__(self, parser_factory):
        self.parser_factory = parser_factory


    def extract_fingerprints(self, software):
        for source_file in software:
            for x in self.extract_fingerprints_(self.parser_factory(source_file)):
                yield x



    @abstractmethod
    def extract_fingerprints_(self, token_iterator):
        raise StopIteration()
