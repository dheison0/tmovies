from typing import List

from . import boitorrent
from .models import Extractor


class ExtractorNotFound(Exception):
    pass


module_as_extractor = lambda m: Extractor(m.TITLE, m.WEBSITE, m.search, m.
                                          download)

extractors = {boitorrent.NAME: module_as_extractor(boitorrent)}


def get_extractor(name: str) -> Extractor | None:
    return extractors.get(name)


def get_extractors() -> List[Extractor]:
    return extractors.values()
