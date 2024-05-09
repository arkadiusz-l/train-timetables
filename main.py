import logging
import os
import re
from datetime import date
from time import sleep
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def get_train_timetable(line):
    print(f"Szukam rozkładu jazdy dla linii {line}...")
    today = get_current_date()
    url = f'https://www.wtp.waw.pl/rozklady-jazdy/?wtp_dt={today}&wtp_md=3&wtp_ln={line}'
    text = f'Rozkład jazdy linii {line} '  # space at the end to bypass S40 line

    logging.debug(f'{today=}')
    logging.debug(f'{url=}')
    logging.debug(f'{text=}')

    links = find_links_with_text(
        url=url,
        text=text
    )

    for link in links:
        file_url = link.get('href')
        filename = link.text + '.pdf'

        downloaded_file_path = os.path.join(DOWNLOADS_DIR, filename)
        if not os.path.exists(downloaded_file_path):  # if file not exists in downloads directory
            download_file(file_url=file_url, downloads_dir=DOWNLOADS_DIR, filename=filename)
        else:
            print(f"Plik '{filename}' już istnieje.")

    print(f"Zakończyłem szukanie rozkładu jazdy dla linii {line}.")


def get_current_date():
    return date.today().strftime("%Y-%m-%d")


def find_links_with_text(url, text):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        pattern = re.compile(text, re.IGNORECASE)
        all_links = soup.find_all('a', string=pattern)
        if all_links:
            return all_links
        else:
            print(f"Nie znaleziono linków zawierających tekst: '{text}'.")
    else:
        print("Nie udało się pobrać strony.")


def download_file(file_url, downloads_dir, filename):
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
    sleep(LATENCY)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    LATENCY = 0.75
    DOWNLOADS_DIR = os.path.abspath(
        os.path.join(os.environ.get('HOMEPATH'), 'Desktop', 'Rozkłady jazdy pociągów')
    )

    get_train_timetable(line='S3')
    get_train_timetable(line='S4')
