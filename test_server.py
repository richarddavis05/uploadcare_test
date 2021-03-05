from contextlib import contextmanager
import pytest

from server import *

TEST_EMODJI = ['&#128507;', '&#128508;']
TEST_WORD_LENGTH = 6


class MockResponse:
    def __init__(self, text, status):
        self._text = text
        self.status = status

    async def text(self):
        return self._text

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


@contextmanager
def does_not_raise():
    yield


async def mock_response_200(test):
    print(test)
    return MockResponse('test', 200)


async def mock_response_404(test):
    print(test)
    return MockResponse('test', 404)


@pytest.mark.asyncio
async def test_get_page_200(mocker):
    expected_text = 'test'
    mocker.patch('aiohttp_requests.requests.get', side_effect=mock_response_200)
    result = await get_page('/test_path')
    assert result == expected_text


@pytest.mark.asyncio
async def test_get_page_404(mocker):
    mocker.patch('aiohttp_requests.requests.get', side_effect=mock_response_404)
    with pytest.raises(web.HTTPClientError):
        await get_page('/test_path')

test_get_content_testdata = [
    (f'<div itemprop="{CONTENT_SELECTOR}" class="post-content js-lh-article" data-io-article-url=""><p>test1</p></div>'
     f'<div><p>test2</p></div>', 'test1', does_not_raise()),
    ('<div class="post-content js-lh-article" data-io-article-url=""><p>test1</p></div><div><p>test2</p></div>', '',
     pytest.raises(web.HTTPClientError))
]


@pytest.mark.asyncio
@pytest.mark.parametrize("page, expected_result, expectation", test_get_content_testdata)
async def test_get_content(page, expected_result, expectation):
    with expectation:
        result = await get_content(page)
        assert result == expected_result

test_modify_content_testdata = [
    ('aaaaaa', f'aaaaaa{TEST_EMODJI[0]}'),
    ('aaaaaa.', f'aaaaaa{TEST_EMODJI[0]}.'),
    ('aaaaaa aaaaaa', f'aaaaaa{TEST_EMODJI[0]} aaaaaa{TEST_EMODJI[1]}'),
    ('aaaaaa aaaaaa aaaaaa', f'aaaaaa{TEST_EMODJI[0]} aaaaaa{TEST_EMODJI[1]} aaaaaa{TEST_EMODJI[0]}')
]


@pytest.mark.asyncio
@pytest.mark.parametrize("content, expected_result", test_modify_content_testdata)
async def test_modify_content(content, expected_result):
    assert await modify_content(content, TEST_WORD_LENGTH) == expected_result
