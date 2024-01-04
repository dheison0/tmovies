from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urlencode


@dataclass(slots=True)
class SearchResult:
    title: str
    url: str
    extractor: str
    thumbnail: Optional[str]
    path: str = None

    def __post_init__(self):
        params = urlencode({"url": self.url})
        self.path = f"/api/download/{self.extractor_id}?{params}"


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
