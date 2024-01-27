from urllib.parse import urljoin

from bs4 import BeautifulSoup, NavigableString

from ..models.classes import Extractor
from ..models.responses import DownloadResult, Link, SearchResult
from ..utils import HTTPBadStatusCode, clear_title, http_get


class ComandoTo(Extractor):
    id = "comandoto"
    title = "Comando Torrent"
    description = "Baixe Filmes e Series torrent HD Lançamentos."
    website = "https://comando.la"

    async def search(self, query: str, page: int = 1) -> list[SearchResult]:
        status, html = await http_get(f"{self.website}/page/{page}/?s={query}")
        if status != 200:
            raise HTTPBadStatusCode(status)
        soup = BeautifulSoup(html, "lxml")
        raw_results = soup.select("article.blog-view")
        results = []
        for raw_result in raw_results:
            raw_title = raw_result.find("h2", class_="entry-title")
            title = clear_title(raw_title.text.strip())
            url = raw_title.find("a").get("href")
            thumbnail = raw_result.find("img").get("src")
            results.append(SearchResult(title, url, self.id, thumbnail))
        return results

    async def download(self, path: str) -> DownloadResult:
        status, html = await http_get(urljoin(self.website, path))
        if status != 200:
            raise HTTPBadStatusCode(status)
        soup = BeautifulSoup(html, "lxml")
        title = soup.select_one("h1.entry-title").text.strip()
        sinopse = soup.select(
            'div.entry-content.cf p strong span[style="color: #0000ff;"]'
        )[-1].parent.parent.text.strip()
        sinopse = " ".join(sinopse.split()[1:])
        thumbnail = soup.select_one("div.entry-content.cf p img").get("src")
        links = self.extract_links(soup)
        return DownloadResult(title, links, thumbnail, sinopse)

    def extract_links(self, soup: NavigableString):
        links = []
        titles = []
        magnets = []

        def mod_and_add_link(link):
            if "magnet:" not in link.magnet or link.magnet in magnets:
                return
            if link.title.lower() in titles:
                link.title += " [LEGENDADO]"
            titles.append(link.title.lower())
            magnets.append(link.magnet)
            links.append(link)

        # With custom buttons
        buttons = soup.select("div.entry-content.cf p a.customButton")
        for button in buttons:
            title = button.parent.find("strong").text.strip()
            url = button.get("href")
            mod_and_add_link(Link(title, url))

        # With button bars
        buttons_bars = soup.select(
            'div.entry-content.cf p[style="text-align: center;"] b'
        )
        for bar in buttons_bars:
            base_title = " ".join([b.text.strip() for b in bar.parent.select("b")])
            for button in bar.parent.select("a"):
                button_title = button.text.strip()
                url = button.get("href")
                mod_and_add_link(Link(f"{base_title} {button_title}", url))

        return links
