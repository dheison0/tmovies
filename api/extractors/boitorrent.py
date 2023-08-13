from typing import List, Tuple

from bs4 import BeautifulSoup, NavigableString

from ..utils import http_get
from .models import DownloadResult, Link, SearchResult

NAME = 'boitorrent'
TITLE = 'BoiTorrent'
WEBSITE = 'https://boitorrent.com'


async def search(query: str, page: int = 1) -> Tuple[List[SearchResult], str]:
    status, html = await http_get(f'{WEBSITE}/torrent-{query}/{page}')
    if status != 200:
        return [], f'website returned {status} status code'
    soup = BeautifulSoup(html, 'lxml')
    items_containers = soup.find_all('div', class_='row semelhantes')
    results = [extract_result(c) for c in items_containers]
    return results, None


def extract_result(container: NavigableString) -> SearchResult:
    raw_title = container.find('strong').text
    title = '-'.join(raw_title.split('-')[:-1]).strip()
    url = container.find('a').get('href')
    thumbnail = container.find('img').get('src')
    return SearchResult(title, url, extractor=NAME, thumbnail=thumbnail)


async def download(url: str) -> Tuple[DownloadResult, str | None]:
    status, html = await http_get(url)
    if status != 200:
        return [], f'website returned {status} status code'
    soup = BeautifulSoup(html, 'lxml')
    sinopse_container = soup.find('div', class_='sinopse')
    title = sinopse_container.find('strong').text.strip()
    sinopse = sinopse_container.find('p').text.replace(title, '').strip()
    thumbnail = soup.find('img',
                          class_='img-responsive capa_imagem').get('src')
    links = extract_links(soup.find('ul', class_='list-group'))
    return DownloadResult(title, links, thumbnail, sinopse), None


def extract_links(container: NavigableString) -> List[Link]:
    extract_link = lambda c: Link(c.text.strip(), c.get('href'))
    links = [extract_link(c) for c in container.find_all('a')]
    return links
