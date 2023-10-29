from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple
from urllib.parse import urlencode


@dataclass
class SearchResult:
    title: str
    url: str
    extractor_id: str
    thumbnail: Optional[str]
    path: str = None

    def __post_init__(self):
        params = urlencode({"url": self.url})
        self.path = f"/download/{self.extractor_id}?{params}"


@dataclass
class ExtractorSearchResult:
    results: list[SearchResult]
    has_more: bool = False
    page: int = 1


@dataclass
class Link:
    title: str
    magnet: str


@dataclass
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
    download: Callable[[str], Tuple[DownloadResult, str | None]]


@dataclass
class ExtractorInfo:
    id: str
    title: str
    description: str
    website: str
