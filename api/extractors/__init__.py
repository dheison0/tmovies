from typing import List

from . import boitorrent
from .models import Extractor

EXTRACTORS = {}


class ExtractorNotFound(Exception):
    pass


def add_extractor(m):
    global EXTRACTORS
    EXTRACTORS[m.NAME] = Extractor(m.NAME, m.TITLE, m.WEBSITE, m.search,
                                   m.download)


add_extractor(boitorrent)


def get_extractor(name: str) -> Extractor | None:
    return EXTRACTORS.get(name)


def get_extractors() -> List[Extractor]:
    return EXTRACTORS.values()
