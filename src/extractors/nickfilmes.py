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
        thumbnail = soup.select_one(".elementor-widget-theme-post-content img").get(
            "data-src"
        )
        links = self.extract_links(soup)
        return DownloadResult(title, links, thumbnail, sinopse)

    def extract_links(self, soup: NavigableString):
        # Disclaimer: If the title is repeated it's because the second one is with captions instead of multi-language

        links = {}
        tag_list = soup.select('p[style="text-align: center;"]')

        def clean_title(t):
            return " ".join(t.strip().split())

        if tag_list[0].find("a"):
            # This will be used if you're downloading a TV show
            for t in tag_list:
                if not t.find("a"):
                    continue
                title = clean_title(t.text)
                magnet = t.find("a").get("href")
                if not magnet:
                    continue
                elif title in links:
                    title += " [Legendado]"
                links[title] = Link(title, magnet)
            return list(links.values())

        # How this part works:
        #  As the website won't create a container for every single link and their titles,
        #  it is needed that you step over "p" tags, I have noted that the first tag is the
        #  title of the link and the second is a container for the button, so I step over
        #  two tags per iteration, extracting content of their and passing away
        i = 0
        while len(tag_list) - i >= 2:
            title = clean_title(tag_list[i].text)
            magnet = tag_list[i + 1].find("a").get("href")
            if title in links:
                title += " [Legendado]"
            links[title] = Link(title, magnet)
            i += 2
        return list(links.values())
