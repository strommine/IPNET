import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import concurrent.futures


# 函数：从URL获取纯英文文本、数字和标点符号
def get_text_from_url(items):
    url, org_name = items
    try:
        response = requests.get(url, timeout=10)  # 设置超时为10秒
        response.raise_for_status()  # 确保请求成功
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):  # 移除所有script和style元素
            script.extract()
        text = soup.get_text()  # 获取纯文本内容
        # 使用正则表达式保留英文文本、数字和标点符号
        clean_text = ' '.join(re.findall(r'[A-Za-z0-9.,;!?]+', text))
        return (url, org_name, clean_text)
    except Exception as e:
        return (url, org_name, None)  # 返回None表示爬取失败


def main():
    MAX_THREADS = 10  # 同时运行的最大线程数量

    with open("D:\\DoAc\\roothtml\\results_filtered.txt", "r", encoding="ISO-8859-1") as f, open(
            "D:\\DoAc\\roothtml\\results_with_text.txt", "w", encoding="ISO-8859-1") as out_f:
        items_list = [eval(line.strip()) for line in f.readlines()]  # 提取所有URL和公司名

        # 使用线程池处理URL
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            results = list(
                tqdm(executor.map(get_text_from_url, items_list), total=len(items_list), desc="Processing URLs"))

            for url, org_name, clean_text in results:
                if clean_text:
                    out_f.write(str([url, org_name, clean_text]) + "\n")


if __name__ == "__main__":
    main()
