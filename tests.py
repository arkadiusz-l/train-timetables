import os
from unittest.mock import patch, MagicMock, mock_open
from main import (
    find_links_on_webpage, parse_pdf_file, get_timetable_from_parsed_pdf, load_config_from_file, save_timetable_to_file,
    LinkNotFound
)
import pytest


def test_load_config_from_file():
    """
    Test loading configuration from a YAML file.

    This test mocks the content of a YAML file and checks if the function
    correctly loads the configuration and returns the expected tuple.
    """
    yaml_path = "test_config.yaml"

    yaml_content = """
    train_lines:
      - Line 1
      - Line 2
    train_stations:
      - Station A
      - Station B
    download_dir: \\path\\to\\download
    output_file_name: output.txt
    latency: 2.5
    """

    with patch('builtins.open', mock_open(read_data=yaml_content)) as mock_file:
        result = load_config_from_file(yaml_path=yaml_path)

    assert result == (
        ['Line 1', 'Line 2'], ['Station A', 'Station B'], 'C:\\path\\to\\download',
        'C:\\path\\to\\download\\output.txt', 2.5
    )


def test_save_timetable_to_file(tmp_path):
    """
    Test saving a timetable to a text file.

    This test creates a temporary file path and saves a sample timetable content
    to the tepomprary text file.
    It then checks if the content was saved correctly.
    """
    timetable = "Sample timetable content."
    output_file_path = os.path.join(tmp_path, "output.txt")

    save_timetable_to_file(timetable=timetable, output_file_path=output_file_path)

    assert os.path.exists(output_file_path)
    with open(output_file_path, 'r', encoding='utf-8') as file:
        saved_content = file.read()

    assert saved_content == timetable


def test_get_timetable_from_parsed_pdf():
    """
    Test extracting timetable from parsed PDF content.

    This test checks if the function correctly extracts the timetable
    for a specific train station from the provided file content.
    """
    train_station = 'station D'
    file_content = ['ROZKŁAD JAZDY S3', 'ważny w dniu 01.06.2024', 'kierunek WARSZAWA', 'STATION A', 'STATION B',
                    'STATION C', 'STATION D o', 'STATION E']
    result = get_timetable_from_parsed_pdf(train_station=train_station, file_content=file_content)

    assert result == 'ROZKŁAD JAZDY S3\nważny w dniu 01.06.2024\nkierunek WARSZAWA\nSTATION D o\n'


def test_parse_pdf_file():
    """
    Test parsing PDF file content.

    This test mocks a PdfReader from PyPDF library and two pages
    with sample text content.
    It checks if the function correctly parses the PDF file
    and returns the combined text from all pages.
    """
    file_path = 'test.pdf'

    with patch('main.PdfReader') as mock_PdfReader:
        mock_reader = MagicMock()
        mock_page_1 = MagicMock()
        mock_page_2 = MagicMock()
        mock_page_1.extract_text.return_value = 'Line 1\nLine 2\nLine 3'
        mock_page_2.extract_text.return_value = 'Line 4\nLine 5'
        mock_reader.pages = [mock_page_1, mock_page_2]
        mock_PdfReader.return_value = mock_reader

        result = parse_pdf_file(file_path)

    assert result == ['Line 1', 'Line 2', 'Line 3', 'Line 4', 'Line 5']


def test_find_links_with_text():
    """
    Test the find_links_with_text function with successful link extraction.

    This test case simulates a successful response from a mock request and checks if the find_links_with_text
    function correctly extracts links with the specified text.
    """
    response_content = """
    <a href='http://example.com/page1'>Link 1</a>
    <a href='http://example.com/page2'>Link 2</a>
    <a href='http://example.com/page3'>Link 3</a>
    """

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = response_content
    mock_get = MagicMock(return_value=mock_response)

    with patch('main.requests.get', mock_get):
        links = find_links_on_webpage(url='http://example.com', text='Link')

    links = [link['href'] for link in links]

    assert links == [
        'http://example.com/page1',
        'http://example.com/page2',
        'http://example.com/page3'
    ]


def test_find_links_with_text_failed():
    """
    Test the find_links_with_text function when no links with the specified text are found.

    This test case simulates a response from a mock request where no links with the specified text are present.
    It checks if the function raises a LinkNotFound exception as expected.
    """
    response_content = """
    <a href='http://example.com/page1'>Aaa 1</a>
    <a href='http://example.com/page2'>Bbb 2</a>
    <a href='http://example.com/page3'>Ccc 3</a>
    """

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = response_content
    mock_get = MagicMock(return_value=mock_response)

    with patch('main.requests.get', mock_get):
        with pytest.raises(LinkNotFound):
            find_links_on_webpage(url='http://example.com', text='Link')
