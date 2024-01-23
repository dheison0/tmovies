from .models.responses import Recommendation
from .utils import http_get, HTTPBadStatusCode, clear_title
from bs4 import BeautifulSoup

RECOMMENDATION_PAGE = "https://comando.la"


async def recommends() -> list[Recommendation]:
    status, html = await http_get(RECOMMENDATION_PAGE)
    if status != 200:
        raise HTTPBadStatusCode(status)

    soup = BeautifulSoup(html, "lxml")
    results = []
    for c in soup.select("article.blog-view"):
        results.append(
            Recommendation(
                title=clear_title(c.find("h2", class_="entry-title").text.strip()),
                thumbnail=c.find("img").get("src").split()[0],
            )
        )
    return results
