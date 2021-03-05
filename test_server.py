import pytest

from server import *


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
