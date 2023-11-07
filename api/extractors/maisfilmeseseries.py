from bs4 import BeautifulSoup

from ..utils import HTTPBadStatusCode, http_get
from .models import DownloadResult, Extractor, ExtractorSearchResult, Link, SearchResult


class MaisFilmesESeries(Extractor):
    id = "maisfilmeseseries"
    title = "Mais Filmes e Series"
    description = "Filmes e Series para download gratuito."
    website = "https://maisfilmeseseries.com"

    async def search(self, query: str, page: int = 1) -> ExtractorSearchResult:
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
            results.append(SearchResult(title, url, self.id, thumbnail))

        pagination_items = soup.select('div[class="paginacao text-center"] ul li')[1:-1]
        has_more = len(pagination_items) > page
        return ExtractorSearchResult(results, has_more, page)

    async def download(self, url: str) -> DownloadResult:
        status, html = await http_get(url)
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
