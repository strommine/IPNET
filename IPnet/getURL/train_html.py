# 获取网页文本final--gpt

import urllib3
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from concurrent.futures import as_completed
import validators
import warnings

from gethtml import *

warnings.filterwarnings("ignore")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

KEYWORDS = ["about", "service", "solution", "who", "do", "it", "us", "our", "company", "do", "network", "online",
            "connect", "coverage", "history", "we"]


# 创建日志输出函数，将日志信息写入对应的文件
def log_to_file(msg):
    # 使用当前线程id作为日志文件名的一部分
    thread_id = threading.get_ident()
    with open(f"D:/DoAc/trainset/logs/log{thread_id}.txt", 'a') as file:
        file.write(msg + '\n')
    # print(msg)


def get_inner_links(url):
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    session = Session()
    session.verify = False
    links = set([url])  # 使用集合代替列表去重
    for attempt in range(3):  # 3 attempts
        try:
            response = session.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            ilinks = [a['href'] for a in soup.find_all('a', href=True)]
            for link in ilinks:
                # 使用urljoin获取完整链接
                full_link = urljoin(url, link)
                # 保留最多6个链接
                if len(links) >= 6:
                    break
                if any(keyword.lower() in link.lower() for keyword in KEYWORDS):
                    links.add(full_link)  # 添加到集合
            return list(links)  # 返回链接列表

        except Exception as e:
            log_to_file(f"尝试第{str(attempt)}次获取网页 {url} 时发生错误: {str(e)}")
            if attempt == 0:  # 第一次失败，等待3秒后重试
                time.sleep(3)
            elif attempt == 1:  # 第二次失败，等待3秒后重试
                time.sleep(3)
            else:  # 第三次失败，返回空列表
                return []

def worker(item):
    try:
        # 获取内页
        url = item[1]
        urls = get_inner_links(url)
        item[1] = urls

        # 获取文本
        unique_urls = set(urls)  # 将URLs转换为集合，从而去除重复项
        texts = []
        for url in unique_urls:
            if validators.url(url):  # 判断URL是否有效
                text = get_web_text(url)
                if text is not None:
                    texts.append(text)
        if not texts:
            return
        combined_text = " ".join(texts)
        item.append(combined_text)

        with open("D:/DoAc/trainset/g-final-set-100.txt", "a", encoding="utf-8") as file:
            file.write(str(item) + "\n")

    except Exception as e:
        log_to_file(f"处理记录 {item} 时发生错误: {str(e)}")


def main():

    with open('D:/DoAc/trainset/g-give-inc.txt', 'r') as file:
        cata = ''
        data = []
        for line in file:
            if line[0] not in '0123456789':
                cata = line.split(':')[0]
            else:
                slist = line.strip().split(' ')
                data.append([slist[1], slist[-1], cata])

    with ThreadPoolExecutor(max_workers=20) as executor:
        # 创建 future 对象列表，待获取列表
        futures = [executor.submit(worker, item) for item in data]
        # 创建进度条
        progress_bar = tqdm(total=len(futures), desc="处理进度")
        for future in as_completed(futures):
            # 进度条每次更新一个
            progress_bar.update(1)
        progress_bar.close()


if __name__ == "__main__":
    main()
