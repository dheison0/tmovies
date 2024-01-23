import logging
from asyncio import gather
from dataclasses import asdict
from http import HTTPStatus

from sanic import Blueprint
from sanic.request import Request
from sanic.response import json

from . import extractors, recommendator, utils

bp = Blueprint("v2-routes")


@bp.route("/recommends")
async def recommendations(_):
    recommends = await recommendator.recommends()
    return json([asdict(r) for r in recommends])


@bp.route("/search", name="Search from all")
@bp.route("/search/<extractor:str>", name="Search from specific")
async def search(request: Request, extractor: str = ""):
    query = request.args.get("q")
    if query is None or not query.strip():
        return json(
            {"error": "invalied query(q) parameter"}, status=HTTPStatus.BAD_REQUEST
        )
    search_extractors = extractors.pool.get_all_extractors()
    if extractor:
        try:
            search_extractors = [extractors.pool.get_extractor(extractor)]
        except extractors.ExtractorNotFound:
            return json({"error": "extractor not found"})

    response = await request.respond(content_type="application/json")
    already_sent = set()

    def filter_not_sent(results):
        to_send = []
        for r in results:
            title = r.title.lower()
            if title in already_sent:
                continue
            to_send.append(r)
            already_sent.add(title)
        return to_send

    async def searcher(extractor):
        try:
            results = await extractor().search(query)
        except Exception as error:
            return logging.error(
                f"Cannot search for '{query}' on '{extractor.id}'", error
            )
        to_send = filter_not_sent(results)
        await gather(*[response.send(utils.dataclass2bytes(s)) for s in to_send])

    searchers = [searcher(e) for e in search_extractors]
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
    if not path:
        return json({"error": "arg 'path' is empty"})
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
