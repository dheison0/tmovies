import logging
from asyncio import gather
from dataclasses import asdict
from http import HTTPStatus
from json import dumps as json_dump

from sanic import Blueprint
from sanic.request import Request
from sanic.response import json

from ..extractors import ExtractorNotFound, pool

bp = Blueprint("v2-routes")


@bp.route("/recommends")
async def recommendations(request: Request):
    extractors = pool.get_all_extractors()
    response = await request.respond()

    async def little_response(data):
        await response.send(json_dump(asdict(data)))

    async def extract(extractor):
        try:
            await extractor().recommendations(little_response)
        except Exception as error:
            logging.error(
                f"Error occurred while trying to retrieve recommendations from {extractor.id}",
                error,
            )

    extractors = [extract(e) for e in extractors]
    await gather(*extractors)


@bp.route("/search")
async def search(request: Request):
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
        body=list(filter(lambda i: i is not None, searchers_results)),
        status=HTTPStatus.OK,
    )


@bp.route("/download")
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
