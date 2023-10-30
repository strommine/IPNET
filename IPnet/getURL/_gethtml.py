import random
import time
from requests import Session
from bs4 import BeautifulSoup
import threading
from urllib.parse import urlparse
from collections import Counter

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


def log_to_file(msg):
    thread_id = threading.get_ident()
    with open(f"D:/DoAc/html/logs/log{thread_id}.txt", 'a') as file:
        file.write(msg + '\n')
    # print(msg)


def preprocess_urls(query, urls):
    words = query.split(' ')
    filtered_urls = [url for url in urls if any(word in url for word in words)
                     and not any(url.endswith(ext) for ext in IGNORED_EXTENSIONS)]
    domains = [urlparse(url).netloc for url in filtered_urls]
    domain_counts = Counter(domains)
    top_domains = [domain for domain, _ in domain_counts.most_common(5)]
    top_urls = [url for url in filtered_urls if urlparse(url).netloc in top_domains]
    return top_urls


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
            text = '\n'.join(chunk for chunk in chunks if chunk)
            return text
        except Exception as e:
            log_to_file(f"尝试第{str(attempt)}次获取网页 {url} 的文本时发生错误: {str(e)}")
            if attempt == 0:  # 第一次失败，等待2秒后重试
                time.sleep(2)
            elif attempt == 1:  # 第二次失败，等待5秒后重试
                time.sleep(5)
            else:  # 第三次失败，返回空字符串
                return None

