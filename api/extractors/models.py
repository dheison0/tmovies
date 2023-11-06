from dataclasses import dataclass
from typing import Callable, List, Optional
from urllib.parse import urlencode


@dataclass(slots=True)
class SearchResult:
    title: str
    url: str
    extractor_id: str
    thumbnail: Optional[str]
    path: str = None

    def __post_init__(self):
        params = urlencode({"url": self.url})
        self.path = f"/api/download/{self.extractor_id}?{params}"


@dataclass(slots=True)
class ExtractorSearchResult:
    results: list[SearchResult]
    has_more: bool = False
    page: int = 1


@dataclass(slots=True)
class Link:
    title: str
    magnet: str


@dataclass(slots=True)
class DownloadResult:
    title: str
    links: List[Link]
    thumbnail: Optional[str]
    sinopse: Optional[str]


class Extractor:
    id: str
    title: str
    description: str
    website: str
    # A function that receives a query followed by the page index(default: 1)
    search: Callable[[str, int], ExtractorSearchResult]
    download: Callable[[str], DownloadResult]


@dataclass(slots=True)
class ExtractorInfo:
    id: str
    title: str
    description: str
    website: str
