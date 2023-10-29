from urllib.parse import urlencode

from bs4 import BeautifulSoup

from ..utils import HTTPBadStatusCode, http_get
from .models import DownloadResult, Extractor, ExtractorSearchResult, Link, SearchResult


class VingadoresTorrent(Extractor):
    id = "vingadorestorrent"
    title = "Vingadores Torrent"
    description = "Vingadores Torrent o seu maior site de torrent do Brasil"
    website = "https://www.vingadorestorrent.com.br"

    async def search(self, query: str, page: int = 1) -> ExtractorSearchResult:
        params = {
            "q": query,
            "start": 0 if page == 1 else page * 10 + 1,
            "max-results": 10,
        }
        status, html = await http_get(f"{self.website}/search?{urlencode(params)}")
        if status != 200:
            raise HTTPBadStatusCode(status)
        soup = BeautifulSoup(html, "lxml")
        raw_results = soup.find_all("article", class_="post hentry")
        results = []
        for raw_result in raw_results:
            container = raw_result.find("h2").find("a")
            title = container.get("title")
            url = container.get("href")
            thumbnail = raw_result.find("img").get("src")
            results += [
                SearchResult(title, url, extractor_id=self.id, thumbnail=thumbnail)
            ]
        return ExtractorSearchResult(page=page, has_more=False, results=results)

    async def download(self, url: str) -> DownloadResult:
        status, html = await http_get(url)
        if status != 200:
            raise HTTPBadStatusCode(status)
        soup = BeautifulSoup(html, "lxml")
        container = soup.find("div", itemprop="description articleBody")
        title = soup.find("h2", class_="post-title entry-title").text.strip()
        sinopse = container.find(
            "span", face="Arial, Helvetica, sans-serif"
        ).text.strip()
        thumbnail = container.find("img").get("src")
        links = []
        for c in container.find_all(
            "a", class_="customButton", rel="noopener noreferrer"
        ):
            links += [Link(c.parent.find("span").text.strip(), c.get("href"))]
        return DownloadResult(title, links, thumbnail, sinopse)
