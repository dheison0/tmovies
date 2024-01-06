from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..models.classes import Extractor
from ..models.responses import DownloadResult, Link, SearchResult
from ..utils import HTTPBadStatusCode, http_get


class BoiTorrent(Extractor):
    id = "boitorrent"
    title = "BoiTorrent"
    description = "Download Lista de Últimos Lançamentos por torrent grátis com qualidade e velocidade diretamente pelo magnet link (Boi Torrent)."
    website = "https://boitorrent.com"

    async def recommendations(self):
        status, html = await http_get(self.website)
        if status != 200:
            raise HTTPBadStatusCode(status)

        def clear_title(t):
            title = t.strip()
            pieces = title.lower().split()
            torrent_location = pieces.index("torrent")
            return " ".join(title.split()[:torrent_location])

        soup = BeautifulSoup(html, "lxml")
        for c in soup.select('li[class="capa_lista text-center"]'):
            yield SearchResult(
                title=clear_title(c.find("h2").text),
                url=c.find("a").get("href"),
                thumbnail=c.find("img").get("src"),
                extractor=self.id,
            )

    async def search(self, query: str, page: int = 1) -> SearchResult:
        status, html = await http_get(
            f"{self.website}/torrent-{query.replace(' ', '_')}/{page}"
        )
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
            results.append(SearchResult(title, url, self.id, thumbnail))

        return results

    async def download(self, path: str) -> DownloadResult:
        status, html = await http_get(urljoin(self.website, path))
        if status != 200:
            raise HTTPBadStatusCode(status)
        soup = BeautifulSoup(html, "lxml")
        sinopse_container = soup.find("div", class_="sinopse")
        title = sinopse_container.find("strong").text.strip()
        sinopse = sinopse_container.find("p").text.replace(title, "").strip()
        thumbnail = soup.find("img", class_="img-responsive capa_imagem").get("src")
        links = [
            Link(a.text.strip(), a.get("href"))
            for a in soup.select('ul[class="list-group"] a')
        ]
        return DownloadResult(title, links, thumbnail, sinopse)
