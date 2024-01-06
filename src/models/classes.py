from typing import AsyncGenerator, Callable

from .responses import DownloadResult, SearchResult


class Extractor:
    id: str
    title: str
    description: str
    website: str

    recommendations: AsyncGenerator
    search: Callable[[str, int], list[SearchResult]]
    download: Callable[[str], DownloadResult]
