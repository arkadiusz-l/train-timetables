import logging
import os
import re
from time import sleep
import requests
import yaml
from bs4 import BeautifulSoup
from pypdf import PdfReader
from tqdm import tqdm
import getpass


class LinkNotFound(Exception):
    """
    Exception raised when a link is not found.

    This exception can be raised when a link is not found on a given webpage.
    """
    pass


def parse_pdf_file(file_path: str) -> list:
    """
    Parse the text content of a PDF file and return it as a list of lines.

    Args:
        file_path (str): The path to the PDF file to be parsed.

    Returns:
        list: A list of lines containing the extracted text content from the PDF file.
    """
    reader = PdfReader(file_path)

    file_content = []
    for page in reader.pages:
        page_content = page.extract_text(
            extraction_mode='layout',
            layout_mode_space_vertically=False,
            layout_mode_scale_weight=1.0
        )

        page_content = page_content.splitlines()
        file_content.extend(page_content)
        logging.debug(f"{file_content=}")
    return file_content


def get_timetable_from_parsed_pdf(train_station: str, file_content: list) -> str:
    """
    Extract train timetable from the parsed PDF file for a given train station.

    Args:
        train_station (str): Name of the station to search for in the timetables.
        file_content (list): The text content of the parsed PDF file containing the timetables.

    Returns:
        str: A train timetable for a given train station.
    """
    train_station = train_station.upper()
    file_lines = file_content
    timetable = ""
    train_line = file_lines[0]
    period = file_lines[1]
    timetable += train_line + '\n'
    timetable += period + '\n'

    for i in range(len(file_lines)):
        file_line = file_lines[i]
        if "kierunek" in file_line:
            direction = file_line
            if train_station not in direction:  # avoids line duplication when the station name is the same as the direction
                timetable += direction + '\n'
        if train_station in file_line:
            if "o" in file_line:
                timetable += file_line + '\n'  # adds a line with train departure
            elif "p" in file_line:
                timetable += file_line + '\n'  # adds a line with train arrival
                next_file_line = file_lines[i+1]
                if "direction" in next_file_line:  # avoids unnecessary line in one-page timetable
                    pass
                elif "o" in next_file_line:
                    timetable += next_file_line + '\n'  # adds a line with train departure

    logging.debug(f'\n{timetable=}')
    return timetable


def save_timetable_to_file(timetable: str, output_file_path: str) -> None:
    """
    Saves a train timetable to a text file.

    Args:
        timetable (str): The text content of the parsed PDF file containing the timetables.
        output_file_path (str): The path to the output file.

    Returns:
        None
    """
    with open(output_file_path, 'a', encoding='utf-8') as file:
        file.write(timetable)
    print(f"Rozkład jazdy został dodany do pliku '{output_file_path}'.\n")


def download_train_timetable_pdf(train_line: str) -> None:
    """
    Download the train timetable for a specific train line.

    Args:
        train_line (str): The train line for which the timetable will be downloaded.

    Returns:
        None
    """
    print(f"Szukam rozkładu jazdy dla linii {train_line}...")
    url = f'https://www.wtp.waw.pl/rozklady-jazdy/?wtp_md=3&wtp_ln={train_line}'
    text = f'Rozkład jazdy linii {train_line} '  # space at the end to bypass S40 line

    logging.debug(f"{url=}")
    logging.debug(f"{text=}")

    links = find_links_on_webpage(
        url=url,
        text=text
    )

    for link in links:
        file_url = link.get('href')
        file_name = link.text + '.pdf'

        downloaded_file_path = os.path.join(download_dir_path, file_name)
        if not os.path.exists(downloaded_file_path):  # if file not exists in download directory
            download_file(file_url=file_url, download_dir_path=download_dir_path, file_name=file_name)
        else:
            print(f"Plik '{file_name}' już istnieje.")
    print(f"Zakończyłem szukanie rozkładu jazdy dla linii {train_line}.")


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


def download_file(file_url: str, download_dir_path: str, file_name: str) -> None:
    """
    Downloads a file from a given URL and save it to the specified directory with the provided file_name.

    Args:
        file_url (str): The URL of the file to download.
        download_dir_path (str): The directory where the file will be saved.
        file_name (str): The name of the file to be saved as.

    Returns:
        None
    """
    logging.debug(f"{file_url=}")

    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        file_length = int(response.headers.get('content-length', 0))
        logging.debug(f"{file_length=}")
        chunk_size = 1024

        os.makedirs(download_dir_path, exist_ok=True)

        download_file_path = os.path.join(download_dir_path, file_name)
        logging.debug(f"{download_file_path=}")

        print(f"Rozpoczynam pobieranie pliku '{file_name}'...")

        with open(download_file_path, 'wb') as file, tqdm(
                desc=file_name,
                total=file_length,
                unit='iB',
                unit_scale=True,
                unit_divisor=chunk_size
        ) as bar:
            for data in response.iter_content(chunk_size=chunk_size):
                size = file.write(data)
                bar.update(size)
        print(f"Pobrano plik: {file_name}.")
    else:
        print(f"Nie udało się pobrać pliku '{file_name}' z lokalizacji: '{file_url}'.")
    sleep(download_latency)


def load_config_from_file(yaml_path: str) -> tuple:
    """
    Loads configuration from a YAML file and assigns it to variables.

    Args:
        yaml_path (str): Path to the YAML configuration file.

    Returns:
        tuple: A tuple containing the following elements:
            - train_lines (list): List of train lines for which the timetable will be downloaded.
            - train_stations (list): List of train stations for which the timetable will be searched.
            - download_dir_path (str): Absolute path to the download directory.
            - output_file_path (str): Path to the output text file.
            - latency (float): Latency after downloading each file.
    """
    with open(yaml_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    train_lines = config['train_lines']
    logging.debug(f"{train_lines=}")

    train_stations = config['train_stations']
    logging.debug(f"{train_stations=}")

    download_dir_name = config['download_dir_name']
    logging.debug(f"{download_dir_name=}")

    output_file_name = config['output_file_name']
    logging.debug(f"{output_file_name=}")

    download_latency = config['download_latency']
    logging.debug(f"{download_latency=}")

    return train_lines, train_stations, download_dir_name, output_file_name, download_latency


def get_user_desktop_path(operating_system: str) -> str:
    """
    Gets the path to the user's "Desktop" directory based on the operating system.

    Args:
        operating_system (str): The operating system for which the path should be returned.
        It can take values 'nt' for Windows or 'posix' for Unix-based systems (Linux, macOS).

    Returns:
        str: The path to the user's "Desktop" directory.
    """
    current_user = getpass.getuser()
    user_desktop_path = ''
    if operating_system == 'nt':  # Windows OS
        user_desktop_path = os.path.join(os.environ.get('HOMEPATH'), 'Desktop')
    elif operating_system == 'posix':  # Linux OS or macOS
        user_desktop_path = os.path.join('/home', current_user, 'Desktop')
    return user_desktop_path


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    pypdf_logger = logging.getLogger('pypdf')
    pypdf_logger.setLevel(logging.ERROR)  # disable WARNING messages from PyPDF library

    train_lines, train_stations, download_dir_name, output_file_name, download_latency = load_config_from_file('config.yaml')

    desktop_path = get_user_desktop_path(operating_system=os.name)
    download_dir_path = os.path.abspath(os.path.join(desktop_path, download_dir_name))
    output_file_path = os.path.abspath(os.path.join(download_dir_path, output_file_name))

    for train_line in train_lines:
        try:
            download_train_timetable_pdf(train_line=train_line)
        except requests.exceptions.ConnectionError:
            print("Błąd połączenia!")
        except LinkNotFound:
            print("Nie znaleziono linków zawierających szukany tekst!")

    for file_name in os.listdir(download_dir_path):
        if file_name.endswith('.pdf'):
            print(f"Przetwarzam plik: {file_name}...")

            file_path = os.path.join(download_dir_path, file_name)
            with open(file_path, 'r'):
                pdf_content = parse_pdf_file(file_path=file_path)

            for train_station in train_stations:
                train_timetable = get_timetable_from_parsed_pdf(train_station=train_station, file_content=pdf_content)
                save_timetable_to_file(timetable=train_timetable, output_file_path=output_file_path)
