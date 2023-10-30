import time

import requests
from bs4 import BeautifulSoup
from langdetect import detect
from googletrans import Translator
import threading

KEYWORDS = ["about", "who", "service", "solution", "who", "do", "it", "us", "our", "company", "do", "network", "online",
            "connect", "coverage", "history"]
INPUT_FILE_PATH = 'D:/DoAc/asdb/Gold/allf.txt'
OUTPUT_FILE_PATH = 'D:/DoAc/asdb/Gold/have-innerurl.txt'
MAX_LINKS = 5


def get_inner_links(domain):
    try:
        urls_to_try = [
            "https://" + domain,
            "https://www." + domain,
            "http://" + domain,
            "http://www." + domain
        ]

        response = None
        for attempt in range(3):
            for url in urls_to_try:
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        break
                except requests.exceptions.RequestException as e:
                    print(f"Error accessing {url}: {e}")

            if response and response.status_code == 200:
                break
            else:
                print(f"Attempt {attempt + 1} failed, retrying in 5 seconds...")
                time.sleep(5)

        if response and response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            links = [a['href'] for a in soup.find_all('a', href=True) if domain in a['href']]
            return links
        else:
            print(f"Failed to access {domain} after 2 attempts.")
            return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []


def process_domain(domain, sublist):
    links = get_inner_links(domain)
    translator = Translator()

    for link in links[:MAX_LINKS]:
        try:
            response = requests.get(link)
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string

            if detect(title) != 'en':
                title = translator.translate(title, dest='en').text

            if any(keyword.lower() in title.lower() for keyword in KEYWORDS):
                sublist.append(link)
                print(f"Added link: {link} with title: {title}")
        except:
            pass


def process_line(line, line_number):
    sublist = eval(line)
    domain = sublist[2][0]
    print(f"Processing line {line_number} with domain: {domain}")
    process_domain(domain, sublist[2])
    print(f"Finished processing line {line_number}")
    return sublist


def main():
    with open(INPUT_FILE_PATH, 'r') as infile, open(OUTPUT_FILE_PATH, 'w') as outfile:
        lines = infile.readlines()
        for line_number, line in enumerate(lines, start=1):
            result_list = process_line(line, line_number)
            outfile.write(str(result_list) + '\n')


if __name__ == "__main__":
    main()
