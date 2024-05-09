import os
import re
import logging
from time import sleep
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def find_links_with_text(url, text):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        pattern = re.compile(text, re.IGNORECASE)
        all_links = soup.find_all('a', string=pattern)
        if all_links:
            return all_links
        else:
            print(f"Nie znaleziono linków zawierających tekst: {text}.")
    else:
        print("Nie udało się pobrać strony.")


def download_file(file_url, downloads_dir, filename):
    logging.debug(f"{file_url=}")

    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        file_length = int(response.headers.get("content-length", 0))
        logging.debug(f"{file_length=}")
        chunk_size = 1024

        download_path = os.path.join(downloads_dir, filename)
        logging.debug(f"{download_path=}")

        os.makedirs(os.path.dirname(download_path), exist_ok=True)

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
        print(f"Pobrano plik: {filename}")
    else:
        print(f"Nie udało się pobrać pliku: {file_url}")
    sleep(LATENCY)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    LATENCY = 0.5
    DOWNLOADS_DIR = os.path.abspath(
        os.path.join(os.environ.get("HOMEPATH"), "Desktop", "Rozkłady jazdy pociągów")
    )

    links = find_links_with_text(
        url="https://www.wtp.waw.pl/rozklady-jazdy/?wtp_dt=2023-03-08&wtp_md=3&wtp_ln=S4",
        text="Rozkład jazdy linii S4 "  # space after "4" to bypass S40 line
    )

    for link in links:
        file_url = link.get('href')
        filename = file_url.split('/')[-1]
        download_file(file_url=file_url, downloads_dir=DOWNLOADS_DIR, filename=filename)
