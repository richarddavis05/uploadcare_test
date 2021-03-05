import re
from itertools import cycle

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp_requests import requests
from bs4 import BeautifulSoup

HOST = 'https://lifehacker.ru'
CONTENT_SELECTOR = 'articleBody'
WORD_LENGTH = 6
EMODJI = ['&#128507;', '&#128508;']


async def get_page(path: str) -> str:
    """Получение http-документа"""
    response = await requests.get(f'{HOST}{path}')
    if not response.status == 200:
        raise web.HTTPClientError(text='Не удалось получить страницу с контентом.')
    text = await response.text()
    return text


async def get_content(page: str) -> str:
    """Получение контента из http-документа"""
    soup = BeautifulSoup(page, 'html.parser')
    try:
        content = soup.find(itemprop=CONTENT_SELECTOR).get_text()
    except AttributeError:
        raise web.HTTPClientError(text='Не найден блок с контентом')
    return content


async def modify_content(content: str, word_length: int) -> str:
    """Подстановка эмоджи."""
    content = re.split(r'\s|\n', content)
    emodji_iter = cycle(EMODJI)
    for idx, word in enumerate(content):
        sanitize_word = await sanitize(word)
        if len(sanitize_word) == word_length:
            content[idx] = word.replace(sanitize_word, ''.join([sanitize_word, next(emodji_iter)]))
    return ' '.join(content)


async def sanitize(word: str) -> str:
    """
    Очистка слова от первого и последнего символа, если они есть.
    Например: «Тест» - вернется Тест.
    """
    if len(word) <= 1:
        return word

    word = list(word)
    special_character_indexes = []
    for character_ind in [len(word) - 1, 0]:
        character = word[character_ind]
        if not character.isalpha() and not character.isdigit():
            special_character_indexes.append(character_ind)

    for special_character_ind in special_character_indexes:
        del word[special_character_ind]

    return ''.join(word)


async def request_handler(request: Request) -> web.Response:
    """Общий обработчик запросов"""
    page = await get_page(request.path)
    content = await get_content(page)
    modified_content = await modify_content(content, WORD_LENGTH)
    return web.Response(text=modified_content, content_type='text/html')


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.get('/', request_handler),
        web.get('/{name}/', request_handler)
    ])
    web.run_app(app, host='localhost', port=9000)
