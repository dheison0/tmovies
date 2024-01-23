from urllib.parse import urljoin

from bs4 import BeautifulSoup, NavigableString

from ..models.classes import Extractor
from ..models.responses import DownloadResult, Link, SearchResult
from ..utils import HTTPBadStatusCode, clear_title, http_get


class NickFilmes(Extractor):
    id = "nickfilmes"
    title = "NickFilmes"
    description = "O Site NickFilmes.net é apenas um agregador de links, nenhum arquivo está hospedado sob nosso domínio."
    website = "https://nickfilmes.net"

    async def search(self, query: str, page: int = 1) -> list[SearchResult]:
        status, html = await http_get(f"{self.website}/?s={query}")
        if status != 200:
            raise HTTPBadStatusCode(status)
        soup = BeautifulSoup(html, "lxml")
        raw_results = soup.find_all("div", class_="elementor-post__card")
        results = []
        for raw_result in raw_results:
            raw_title = raw_result.find("h3", class_="elementor-post__title")
            url = raw_title.find("a").get("href")
            thumbnail = raw_result.find("img").get("src")
            results.append(
                SearchResult(clear_title(raw_title.text), url, self.id, thumbnail)
            )

        return results

    async def download(self, path: str) -> DownloadResult:
        status, html = await http_get(urljoin(self.website, path))
        if status != 200:
            raise HTTPBadStatusCode(status)
        soup = BeautifulSoup(html, "lxml")
        title = soup.find(
            "h2", class_="elementor-heading-title elementor-size-default"
        ).text.strip()
        sinopse_container = soup.find_all("span", style="color: #0000ff;")[-1].parent
        sinopse = sinopse_container.text.replace(
            sinopse_container.find("span").text, ""
        ).strip()
        thumbnail = soup.find("meta", property="og:image").get("content")
        if not thumbnail:
            thumbnail = soup.select_one("p img.size-full").get("src")
        links = self.extract_links(soup)
        return DownloadResult(title, links, thumbnail, sinopse)

    def extract_links(self, soup: NavigableString) -> list[Link]:
        buttons = soup.select("a")
        link_titles = []
        links = []
        for button in buttons:
            url = button.get("href")
            if not url or "magnet:" not in url:
                continue
            title = button.text.strip()
            if title.lower() in link_titles or "tgx" in url.lower():
                title += " [LEGENDADO]"
            links.append(Link(title, magnet=url))
            link_titles.append(title.lower())
        return links
