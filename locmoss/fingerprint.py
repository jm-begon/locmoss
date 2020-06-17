from abc import ABCMeta, abstractmethod


class Fingerprinter(object, metaclass=ABCMeta):

    def __init__(self, parser_factory):
        self.parser_factory = parser_factory


    def extract_fingerprints(self, software):
        for source_file in software:
            yield self.extract_fingerprints_(self.parser_factory(source_file))


    @abstractmethod
    def extract_fingerprints_(self, token_iterator):
        pass
