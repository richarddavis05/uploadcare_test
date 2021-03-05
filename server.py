from aiohttp import web
from aiohttp.web_request import Request


async def request_handler(request: Request) -> web.Response:
    """Общий обработчик запросов"""
    return web.Response(text='test', content_type='text/html')


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.get('/', request_handler),
        web.get('/{name}/', request_handler)
    ])
    web.run_app(app, host='localhost', port=9000)
