import json
import random
import time
import socket
import ssl
from urllib.parse import urlparse

from requests import Session
from bs4 import BeautifulSoup
import threading
from langdetect import detect
from googletrans import Translator

IGNORED_EXTENSIONS = ['.pdf']
USER_AGENTS = [
    # Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 '
    'Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 '
    'Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile '
    'Safari/537.36',

    # Firefox
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Android 10; Mobile; rv:68.0) Gecko/68.0 Firefox/68.0',

    # Safari
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 '
    'Safari/605.1.15',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 '
    'Mobile/15E148 Safari/604.1',

    # Edge
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 '
    'Safari/537.36 Edg/91.0.864.59',

    # Opera
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 '
    'Safari/537.36 OPR/62.0.3331.72',
    'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Mobile '
    'Safari/537.36 OPR/62.0.3331.72',
]


def load_and_process_data(data_file):
    with open(data_file, 'r') as file:
        data = [json.loads(line.strip()) for line in file.readlines()]
    return data


def log_to_file(msg):
    thread_id = threading.get_ident()
    with open(f"D:/DoAc/html/logs/log{thread_id}.txt", 'a') as file:
        file.write(msg + '\n')
    # print(msg)


def translate_to_english(text):
    translator = Translator()
    try:
        return translator.translate(text, dest='en').text
    except Exception as e:
        log_to_file(f"翻译错误: {str(e)}")
        return text


def get_web_text(url):
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    session = Session()
    session.verify = False
    for attempt in range(3):
        try:
            res = session.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            # 检查是否为英文
            if detect(text) != 'en':
                text = translate_to_english(text)

            return text

        except Exception as e:
            log_to_file(f"尝试第{str(attempt)}次获取网页 {url} 的文本时发生错误: {str(e)}")
            if attempt == 0:  # 第一次失败，等待2秒后重试
                time.sleep(2)
            elif attempt == 1:  # 第二次失败，等待5秒后重试
                time.sleep(2)
            else:  # 第三次失败，返回空字符串
                return None


def get_certificate_organization(url):
    domain = urlparse(url).netloc
    context = ssl.create_default_context()
    conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=domain)
    conn.settimeout(3.0)  # 超时时间
    conn.connect((domain, 443))
    cert = conn.getpeercert()
    conn.close()

    for field in cert['subject']:
        attribute_type, attribute_value = field[0]
        if attribute_type == 'organizationName':
            return attribute_value
    return None