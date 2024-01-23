from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..models.classes import Extractor
from ..models.responses import DownloadResult, Link, SearchResult
from ..utils import HTTPBadStatusCode, clear_title, http_get


class MaisFilmesESeries(Extractor):
    id = "maisfilmeseseries"
    title = "Mais Filmes e Series"
    description = "Filmes e Series para download gratuito."
    website = "https://maisfilmeseseries.com"

    async def search(self, query: str, page: int = 1) -> SearchResult:
        status, html = await http_get(
            f"{self.website}/{query.replace(' ', '_')}/pagina/{page}/"
        )
        if status != 200:
            raise HTTPBadStatusCode(status)
        soup = BeautifulSoup(html, "lxml")

        results = []
        for raw_result in soup.select('div[id="lista"] div[class="post"]'):
            link = raw_result.select_one('div[class="titulo_post"] a')
            title = link.text.strip()
            url = link.get("href")
            thumbnail = raw_result.find("img").get("src")
            results.append(SearchResult(clear_title(title), url, self.id, thumbnail))

        return results

    async def download(self, path: str) -> DownloadResult:
        status, html = await http_get(urljoin(self.website, path))
        if status != 200:
            raise HTTPBadStatusCode(status)
        soup = BeautifulSoup(html, "lxml")
        title = soup.select_one('h2[class="h5"]').text.strip()

        sinopse_container = soup.select_one('p[class="text-justify"]')
        sinopse_title = sinopse_container.find("strong").text
        sinopse = sinopse_container.text.replace(sinopse_title + ".", "").strip()

        thumbnail = soup.select_one('img[class="img-fluid poster mx-auto"]').get("src")
        links = [
            Link(a.get("title").strip(), a.get("href"))
            for a in soup.select('p[id="lista_download"] a')
        ]
        return DownloadResult(title, links, thumbnail, sinopse)
