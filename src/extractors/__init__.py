from ..models.classes import Extractor
from . import boitorrent, comandoto, maisfilmeseseries, nickfilmes


class ExtractorNotFound(Exception):
    def __init__(self, id: str):
        super().__init__(f"Extractor id '{id}' not found!")


class Pool:
    def __init__(self):
        self.extractors = {}

    def add_extractor(self, extractor: Extractor):
        self.extractors[extractor.id] = extractor

    def get_extractor(self, id: str) -> Extractor:
        if extractor := self.extractors.get(id):
            return extractor
        raise ExtractorNotFound(id)

    def get_all_extractors(self) -> list[Extractor]:
        return self.extractors.values()


pool = Pool()
pool.add_extractor(boitorrent.BoiTorrent)
pool.add_extractor(nickfilmes.NickFilmes)
pool.add_extractor(maisfilmeseseries.MaisFilmesESeries)
pool.add_extractor(comandoto.ComandoTo)
