import logging
import os
import re
from time import sleep
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from tqdm import tqdm


class LinkNotFound(Exception):
    """
    Exception raised when a link is not found.

    This exception can be raised when a link is not found on a given webpage.
    """
    pass


def parse_pdf_file(filepath: str) -> list:
    """
    Parse the text content of a PDF file and return it as a list of lines.

    Args:
        filepath (str): The path to the PDF file to be parsed.

    Returns:
        list: A list of lines containing the extracted text content from the PDF file.
    """
    reader = PdfReader(filepath)

    for page in reader.pages:
        content = page.extract_text(
            extraction_mode='layout',
            layout_mode_space_vertically=False,
            layout_mode_scale_weight=1.0
        )

        content = content.splitlines()
        logging.debug(f"{content=}")
        return content


def get_timetables(station: str, file_content: list) -> None:
    """
    Extract train timetables from the specified PDF file for a given train station.

    Args:
        station (str): Name of the station to search for in the timetables.
        file_content (str): The content of the PDF file containing the timetables.
    """
    station = station.upper()
    file_lines = file_content

    train_line = file_lines[0]
    period = file_lines[1]
    print(train_line)
    print(period)

    for i in range(len(file_lines)):
        file_line = file_lines[i]

        if "kierunek" in file_line:
            direction = file_line
            print(direction)

        if station in file_line:
            if "o" in file_line:
                print(file_line)
            elif "p" in file_line:
                print(file_line)
                next_file_line = file_lines[i+1]
                if "o" in next_file_line:
                    print(next_file_line)


def download_train_timetable(line: str) -> None:
    """
    Download the train timetable for a specific train line.

    Args:
        line (str): The train line for which to retrieve the timetable.

    Returns:
        None
    """
    print(f"Szukam rozkładu jazdy dla linii {line}...")
    url = f'https://www.wtp.waw.pl/rozklady-jazdy/?wtp_md=3&wtp_ln={line}'
    text = f'Rozkład jazdy linii {line} '  # space at the end to bypass S40 line

    logging.debug(f'{url=}')
    logging.debug(f'{text=}')

    links = find_links_on_webpage(
        url=url,
        text=text
    )

    for link in links:
        file_url = link.get('href')
        filename = link.text + '.pdf'

        downloaded_file_path = os.path.join(downloads_dir, filename)
        if not os.path.exists(downloaded_file_path):  # if file not exists in downloads directory
            download_file(file_url=file_url, downloads_dir=downloads_dir, filename=filename)
        else:
            print(f"Plik '{filename}' już istnieje.")

    print(f"Zakończyłem szukanie rozkładu jazdy dla linii {line}.")


def find_links_on_webpage(url: str, text: str) -> list:
    """
    Finds all links on a webpage that contain a specific text.

    Args:
        url (str): The URL of the webpage to search for links.
        text (str): The text to search for in the links.

    Returns:
        list: A list of links containing the specified text.

    Raises:
        LinkNotFound: If no links containing the specified text are found.
    """
    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')
    pattern = re.compile(text, re.IGNORECASE)
    all_links = soup.find_all('a', string=pattern)
    if all_links:
        return all_links
    raise LinkNotFound


def download_file(file_url: str, downloads_dir: str, filename: str) -> None:
    """
    Downloads a file from a given URL and save it to the specified directory with the provided filename.

    Args:
        file_url (str): The URL of the file to download.
        downloads_dir (str): The directory where the file will be saved.
        filename (str): The name of the file to be saved as.

    Returns:
        None
    """
    logging.debug(f'{file_url=}')

    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        file_length = int(response.headers.get('content-length', 0))
        logging.debug(f'{file_length=}')
        chunk_size = 1024

        download_path = os.path.join(downloads_dir, filename)
        logging.debug(f'{download_path=}')

        os.makedirs(os.path.dirname(download_path), exist_ok=True)

        print(f"Rozpoczynam pobieranie pliku '{filename}'...")

        with open(download_path, 'wb') as file, tqdm(
                desc=filename,
                total=file_length,
                unit='iB',
                unit_scale=True,
                unit_divisor=chunk_size
        ) as bar:
            for data in response.iter_content(chunk_size=chunk_size):
                size = file.write(data)
                bar.update(size)
        print(f"Pobrano plik: {filename}.")
    else:
        print(f"Nie udało się pobrać pliku '{filename}' z lokalizacji: '{file_url}'.")
    sleep(latency)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    pypdf_logger = logging.getLogger('pypdf')
    pypdf_logger.setLevel(logging.ERROR)  # disable WARNING messages from PyPDF library
    latency = 0.75
    downloads_dir = os.path.abspath(
        os.path.join(os.environ.get('HOMEPATH'), 'Desktop', 'Rozkłady jazdy pociągów')
    )

    try:
        download_train_timetable(line='S3')
        download_train_timetable(line='S4')
    except requests.exceptions.ConnectionError:
        print("Błąd połączenia!")
    except LinkNotFound:
        print("Nie znaleziono linków zawierających szukany tekst!")
