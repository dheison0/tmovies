from typing import Callable

from .responses import DownloadResult, SearchResult


class Extractor:
    id: str
    title: str
    description: str
    website: str

    search: Callable[[str, int], list[SearchResult]]
    download: Callable[[str], DownloadResult]
