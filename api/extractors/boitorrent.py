from bs4 import BeautifulSoup

from ..utils import HTTPBadStatusCode, http_get
from .models import DownloadResult, Extractor, ExtractorSearchResult, Link, SearchResult


class BoiTorrent(Extractor):
    id = "boitorrent"
    title = "BoiTorrent"
    description = "Download Lista de Últimos Lançamentos por torrent grátis com qualidade e velocidade diretamente pelo magnet link (Boi Torrent)."
    website = "https://boitorrent.com"

    async def search(self, query: str, page: int = 1) -> ExtractorSearchResult:
        status, html = await http_get(f"{self.website}/torrent-{query}/{page}")
        if status != 200:
            raise HTTPBadStatusCode(status)
        soup = BeautifulSoup(html, "lxml")
        raw_results = soup.find_all("div", class_="row semelhantes")
        results = []
        for raw_result in raw_results:
            raw_title = raw_result.find("strong").text
            title = "-".join(raw_title.split("-")[:-1]).strip()
            url = raw_result.find("a").get("href")
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
        sinopse_container = soup.find("div", class_="sinopse")
        title = sinopse_container.find("strong").text.strip()
        sinopse = sinopse_container.find("p").text.replace(title, "").strip()
        thumbnail = soup.find("img", class_="img-responsive capa_imagem").get("src")
        links = []
        for a in soup.find("ul", class_="list-group").find_all("a"):
            links += [Link(a.text.strip(), a.get("href"))]
        return DownloadResult(title, links, thumbnail, sinopse)
