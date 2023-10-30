import random
import time

import requests
from requests import Session
from bs4 import BeautifulSoup
import threading
from collections import Counter
from urllib.parse import urlparse, urljoin

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
    with open(f"D:/DoAc/real/logs/log{thread_id}.txt", 'a') as file:
        file.write(msg + '\n')
    # print(msg)


def perform_search(query):
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    session = Session()
    session.verify = False
    urls = []

    for start in range(0, 50, 10):
        url = "https://www.google.com/search?q=" + query + "&start=" + str(start)
        for attempt in range(3):
            try:
                res = session.get(url, headers=headers, timeout=10)  # 设置超时时间为10秒
                soup = BeautifulSoup(res.text, 'html.parser')
                anchors = soup.find_all('a')
                for anchor in anchors:
                    try:
                        link = anchor['href']
                        log_to_file(f"获取到anchor  {anchor}")
                        log_to_file(f"获取到link  {link}")
                        if link.startswith("/url?q="):
                            link = link.split("?q=")[1].split("&")[0]
                        if link.startswith('//'):
                            link = 'https:' + link  # 选择使用https，或者根据需要改为http
                            urls.append(link)
                    except KeyError:
                        continue
                    if len(urls) >= 50:
                        break
                log_to_file(f"获取到{urls}")
            except Exception as e:
                log_to_file(f"尝试第{str(attempt)}次访问 {url} 时发生错误: {str(e)}")
                if attempt == 0:  # 第一次失败，等待2秒后重试
                    time.sleep(2)
                elif attempt == 1:  # 第二次失败，等待5秒后重试
                    time.sleep(2)
    return urls[:50]


def preprocess_urls2(query, urls):
    # words = query.split(' ')
    # filtered_urls = [url for url in urls if any(word in url for word in words)
    #                  and not any(url.endswith(ext) for ext in IGNORED_EXTENSIONS)]
    domains_with_scheme = ["{}://{}".format(urlparse(url).scheme, urlparse(url).netloc) for url in urls]
    domain_counts = Counter(domains_with_scheme)
    top_domains = [domain for domain, _ in domain_counts.most_common(5)]
    return top_domains


KEYWORDS = ["about", "who", "service", "solution", "who", "do", "it", "us", "our",
            "company", "do", "network", "online", "connect", "coverage", "history"]
COMMON_DOMAIN_BLACKLIST = [
    "https://support.google.com",
    "https://www.google.com",
    "https://policies.google.com",
    "https://maps.google.com",
    "https://accounts.google.com",
    "https://translate.google.com",
    "https://search.app.goo.gl",
    "https://www.facebook.com",
    "https://en.wikipedia.org",
    "https://www.youtube.com",
    "https://m.facebook.com",
    "https://www.linkedin.com",
    "https://www.instagram.com",
    "https://twitter.com",
    "https://m.youtube.com",
    "https://en.m.wikipedia.org",
    "https://www.reddit.com",
    "http://en.wikipedia.org",
    "https://www.crunchbase.com",
    "https://github.com",
    "https://www.amazon.com",
    "https://sites.ipaddress.com",
    "https://bgp.he.net",
    "https://www.whois.com",
    "https://play.google.com",
    "https://dnslytics.com",
    "https://myip.ms",
    "https://www.cubdomain.com",
    "https://ipinfo.io",
    "https://www.tiktok.com"
]


def preprocess_urls(urls):
    domains_with_scheme = ["{}://{}".format(urlparse(url).scheme, urlparse(url).netloc) for url in urls]
    domain_counts = Counter(domains_with_scheme)

    top_domain = None
    for domain, _ in domain_counts.most_common():
        if domain not in COMMON_DOMAIN_BLACKLIST:
            top_domain = domain
            break

    internal_links_to_crawl = []

    if top_domain:
        with requests.Session() as session:
            try:
                response = session.get(top_domain)
                soup = BeautifulSoup(response.content, 'html.parser')
                for link in soup.find_all('a', href=True):
                    # 内页url
                    full_url = urljoin(top_domain, link['href'])

                    # 使用链接title或者本身
                    title = link.get('title') or link.text
                    if any(keyword in title.lower() for keyword in KEYWORDS):
                        internal_links_to_crawl.append(full_url)

                    # 获取5条
                    if len(internal_links_to_crawl) >= 5:
                        break
            except Exception as e:
                log_to_file(f"获取内页时发生错误 {top_domain}: {e}")

    return [top_domain] + internal_links_to_crawl if top_domain else internal_links_to_crawl
