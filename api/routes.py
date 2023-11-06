import logging
from asyncio import gather
from dataclasses import asdict
from http import HTTPStatus

from sanic import Sanic
from sanic.request import Request
from sanic.response import json

from .extractors import ExtractorNotFound, pool
from .utils import check_queries


def add_all(app: Sanic):
    app.add_route(
        name="search_with_all",
        handler=check_queries(search_with_all, ["query"]),
        uri="/api/search/all",
    )
    app.add_route(
        name="search_using",
        handler=check_queries(search, ["query"]),
        uri="/api/search/<extractor_id>",
    )
    app.add_route(
        name="download_using",
        handler=check_queries(download, ["url"]),
        uri="/api/download/<extractor_id>",
    )


async def search(request: Request, extractor_id: str):
    try:
        extractor = pool.get_extractor(extractor_id)
    except ExtractorNotFound:
        return json(
            body={"error": f'extractor "{extractor_id}" not found'},
            status=HTTPStatus.NOT_FOUND,
        )
    query = request.args.get("query")
    page = int(request.args.get("page", 1))
    try:
        response = await extractor().search(query, page)
    except Exception as error:
        logging.error(
            f"Failed to extract results of '{query}' from '{extractor_id}' page {page}",
            error,
        )
        return json(
            body={"error": f"extractor error: {error}"},
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    return json(body=asdict(response), status=HTTPStatus.OK)


async def search_with_all(request: Request):
    query = request.args.get("query")

    async def searcher(e):
        extractor = pool.get_extractor(e.id)
        try:
            result = await extractor().search(query)
        except Exception as error:
            logging.error(f"Failed to search for '{query}' on '{e.id}'", error)
            return
        return {
            "extractor_id": extractor.id,
            "extractor_title": extractor.title,
            "response": asdict(result),
        }

    searchers = [searcher(e) for e in pool.get_all_extractors()]
    searchers_results = await gather(*searchers)
    return json(
        body=searchers_results,
        status=HTTPStatus.OK,
    )


async def download(request: Request, extractor_id: str):
    try:
        extractor = pool.get_extractor(extractor_id)
    except ExtractorNotFound:
        return json(
            body={"error": f'extractor "{extractor_id}" not found'},
            status=HTTPStatus.NOT_FOUND,
        )
    url = request.args.get("url")
    try:
        result = await extractor().download(url)
    except Exception as exception:
        error_message = (
            f"Error raised while trying to get download information from url '{url}'"
        )
        logging.error(error_message, exception)
        return json(
            body={"error": f"{error_message}: {str(exception)}"},
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    return json(body=asdict(result), status=HTTPStatus.OK)
