from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urlencode, urlparse


@dataclass(slots=True)
class SearchResult:
    title: str
    url: str
    extractor: str
    thumbnail: Optional[str]
    next: str = None

    def __post_init__(self):
        parsed_url = urlparse(self.url)
        params = {"path": parsed_url.path}
        if parsed_url.params:
            params.path += f"?{parsed_url.params}"
        self.next = f"/download/{self.extractor}?{urlencode(params)}"


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


@dataclass(slots=True)
class Recommendation:
    title: str
    thumbnail: str
