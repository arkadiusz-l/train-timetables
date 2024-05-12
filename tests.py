from unittest.mock import patch, MagicMock
from main import find_links_with_text, LinkNotFound
import pytest


def test_find_links_with_text():
    """
    Test the find_links_with_text function with successful link extraction.

    This test case simulates a successful response from a mock request and checks if the find_links_with_text
    function correctly extracts links with the specified text.
    """
    response_content = """
    <a href="http://example.com/page1">Link 1</a>
    <a href="http://example.com/page2">Link 2</a>
    <a href="http://example.com/page3">Link 3</a>
    """

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = response_content
    mock_get = MagicMock(return_value=mock_response)

    with patch('main.requests.get', mock_get):
        links = find_links_with_text("http://example.com", "Link")

    links = [link['href'] for link in links]

    assert links == [
        "http://example.com/page1",
        "http://example.com/page2",
        "http://example.com/page3"
    ]


def test_find_links_with_text_failed():
    """
    Test the find_links_with_text function when no links with the specified text are found.

    This test case simulates a response from a mock request where no links with the specified text are present.
    It checks if the function raises a LinkNotFound exception as expected.
    """
    response_content = """
    <a href="http://example.com/page1">Aaa 1</a>
    <a href="http://example.com/page2">Bbb 2</a>
    <a href="http://example.com/page3">Ccc 3</a>
    """

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = response_content
    mock_get = MagicMock(return_value=mock_response)

    with patch('main.requests.get', mock_get):
        with pytest.raises(LinkNotFound):
            find_links_with_text("http://example.com", "Link")
