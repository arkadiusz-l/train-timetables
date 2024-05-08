import re
import logging
from time import sleep
import requests
from bs4 import BeautifulSoup


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


def download_file(file_url):
    logging.debug(f"{file_url=}")

    filename = file_url.split('/')[-1]
    print(f"Pobieram plik: {filename}...")

    response = requests.get(file_url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
            print(f"Pobrano plik: {filename}")
    else:
        print(f"Nie udało się pobrać pliku: {file_url}")
    sleep(LATENCY)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    LATENCY = 0.5

    links = find_links_with_text(
        url="https://www.wtp.waw.pl/rozklady-jazdy/?wtp_dt=2023-03-08&wtp_md=3&wtp_ln=S4",
        text="dni powszednie"
    )

    for link in links:
        download_file(link.get('href'))
