import logging
from asyncio import gather
from dataclasses import asdict
from http import HTTPStatus
from json import dumps as json_dump

from sanic import Blueprint
from sanic.request import Request
from sanic.response import json

from .. import extractors

bp = Blueprint("v2-routes")


@bp.route("/recommends")
async def recommendations(request: Request):
    extractors = extractors.pool.get_all_extractors()
    response = await request.respond()

    sent_titles = set()

    async def extract(extractor):
        try:
            async for r in extractor().recommendations():
                old_size = len(sent_titles)
                sent_titles.add(r.title.lower())
                new_size = len(sent_titles)
                if old_size != new_size:
                    await response.send(json_dump(asdict(r)))
        except Exception as error:
            logging.error(
                f"Error retrieving recommendations from {extractor.title}",
                error,
            )

    extractors = [extract(e) for e in extractors]
    await gather(*extractors)


@bp.route("/search")
async def search(request: Request):
    query = request.args.get("q")
    if query is None or query.strip() == "":
        return json(
            {"error": "invalied query(q) parameter"}, status=HTTPStatus.BAD_REQUEST
        )
    response = await request.respond()

    async def searcher(e):
        extractor = extractors.pool.get_extractor(e.id)
        try:
            result = await extractor().search(query)
        except Exception as error:
            logging.error(f"Failed to search for '{query}' on '{e.id}'", error)
            return
        await response.send(
            json_dump(
                {"extractor": extractor.title, "results": [asdict(r) for r in result]}
            )
        )

    searchers = [searcher(e) for e in extractors.pool.get_all_extractors()]
    await gather(*searchers)


@bp.route("/download/<extractor_id:str>")
async def download(request: Request, extractor_id: str):
    try:
        extractor = extractors.pool.get_extractor(extractor_id)
    except extractors.ExtractorNotFound:
        return json(
            body={"error": f'extractor "{extractor_id}" not found'},
            status=HTTPStatus.NOT_FOUND,
        )
    path = request.args.get("path")
    try:
        result = await extractor().download(path)
    except Exception as exception:
        error_message = (
            f"Error getting download information from {extractor.title} {path}"
        )
        logging.error(error_message, exception)
        return json(
            body={"error": f"{error_message}: {str(exception)}"},
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    return json(body=asdict(result), status=HTTPStatus.OK)
