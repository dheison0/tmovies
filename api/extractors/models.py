from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple
from urllib.parse import urlencode


@dataclass
class SearchResult:
    title: str
    url: str
    extractor: str
    thumbnail: Optional[str]
    api_path: str = None

    def __post_init__(self):
        params = urlencode({'url': self.url})
        self.api_path = f'/{self.extractor.lower()}/get?{params}'


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


@dataclass
class Extractor:
    title: str
    website_url: str
    # A function that receives a query followed by the page index(default: 1)
    search: Callable[[str, int], List[SearchResult]]
    download: Callable[[str], Tuple[DownloadResult, str | None]]
    name: str = None

    def __post_init(self):
        self.name = self.name or self.__name__
