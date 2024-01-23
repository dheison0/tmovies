import logging
from asyncio import gather
from dataclasses import asdict
from http import HTTPStatus
from json import dumps as json_dump
from . import recommendator

from sanic import Blueprint
from sanic.request import Request
from sanic.response import json

from . import extractors

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
    if extractor:
        try:
            search_extractors = [extractors.pool.get_extractor(extractor)]
        except extractors.ExtractorNotFound:
            return json({"error": "extractor not found"})
    else:
        search_extractors = extractors.pool.get_all_extractors()

    response = await request.respond()
    sent_titles = set()

    def filter_unrepeated(results):
        unrepeated = []
        for r in results:
            old_size = len(sent_titles)
            sent_titles.add(r.title.lower())
            new_size = len(sent_titles)
            if old_size < new_size:
                unrepeated.append(r)
        return unrepeated

    def dataclass2bytes(data):
        data_dict = asdict(data)
        data_json = json_dump(data_dict)
        return data_json.encode()

    async def searcher(e):
        extractor = extractors.pool.get_extractor(e.id)
        try:
            results = await extractor().search(query)
        except Exception as error:
            logging.error(f"Failed to search for '{query}' on '{e.id}'", error)
            return
        unrepeated = filter_unrepeated(results)
        await gather(*[response.send(dataclass2bytes(i)) for i in unrepeated])

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
