from . import boitorrent, nickfilmes, vingadorestorrent
from .models import Extractor, ExtractorInfo


class ExtractorNotFound(Exception):
    def __init__(self, id: str):
        super().__init__(f"Extractor id '{id}' not found!")


class Pool:
    def __init__(self):
        self.extractors = {}

    def add_extractor(self, extractor: Extractor):
        self.extractors[extractor.id] = extractor

    def get_extractor(self, id: str) -> Extractor:
        extractor = self.extractors.get(id)
        if extractor:
            return extractor
        raise ExtractorNotFound(id)

    def get_all_extractors(self) -> list[ExtractorInfo]:
        extractors = [
            ExtractorInfo(e.id, e.title, e.description, e.website)
            for _, e in self.extractors.items()
        ]
        return extractors


pool = Pool()
pool.add_extractor(boitorrent.BoiTorrent)
pool.add_extractor(vingadorestorrent.VingadoresTorrent)
pool.add_extractor(nickfilmes.NickFilmes)
