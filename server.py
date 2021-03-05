from aiohttp import web
from aiohttp.web_request import Request
from aiohttp_requests import requests

HOST = 'https://lifehacker.ru'


async def get_page(path: str) -> str:
    """Получение http-документа"""
    response = await requests.get(f'{HOST}{path}')
    if not response.status == 200:
        raise web.HTTPClientError(text='Не удалось получить страницу с контентом.')
    text = await response.text()
    return text


async def request_handler(request: Request) -> web.Response:
    """Общий обработчик запросов"""
    page = await get_page(request.path)
    return web.Response(text='test', content_type='text/html')


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.get('/', request_handler),
        web.get('/{name}/', request_handler)
    ])
    web.run_app(app, host='localhost', port=9000)
