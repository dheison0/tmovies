from asyncio import gather
from dataclasses import asdict
from http import HTTPStatus

from sanic import Sanic
from sanic.request import Request
from sanic.response import json

from .extractors import get_extractor, get_extractors
from .utils import check_queries


def add_all(app: Sanic):
    app.add_route(name='search_with_all',
                  handler=check_queries(search_with_all, ['query']),
                  uri='/search')
    app.add_route(name='search_using',
                  handler=check_queries(search, ['query']),
                  uri='/search/<extractor_name>')
    app.add_route(name='download_using',
                  handler=check_queries(download, ['url']),
                  uri='/download/<extractor_name>')


async def search(request: Request, extractor_name: str):
    extractor = get_extractor(extractor_name)
    if extractor is None:
        return json(body={'error': f'extractor "{extractor_name}" not found'},
                    status=HTTPStatus.NOT_FOUND)
    query = request.args.get('query')
    page = int(request.args.get('page', 1))
    results, error = await extractor.search(query, page)
    if error is not None:
        return json(body={'error': f'extractor error: {error}'},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR)
    return json(body={'results': [asdict(i) for i in results]},
                status=HTTPStatus.OK)


async def search_with_all(request: Request):
    query = request.args.get('query')

    async def searcher(e):
        result, error = await e.search(query)
        return {'extractor': e.name, 'result': result, 'error': error}

    searchers = [searcher(e) for e in get_extractors()]
    searchers_result = await gather(*searchers)
    results = []
    errors = []
    for r in searchers_result:
        if r['error']:
            errors += [{'extractor': r['extractor'], 'error': r['error']}]
        else:
            results += r['result']
    return json(body={
        'errors': errors,
        'results': [asdict(r) for r in results]
    },
                status=HTTPStatus.OK)


async def download(request: Request, extractor_name: str):
    extractor = get_extractor(extractor_name)
    if extractor is None:
        return json(body={'error': f'extractor "{extractor_name}" not found'},
                    status=HTTPStatus.NOT_FOUND)
    url = request.args.get('url')
    result, error = await extractor.download(url)
    if error:
        return json(body={'error': f'extractor error: {error}'},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR)
    return json(body=asdict(result), status=HTTPStatus.OK)
