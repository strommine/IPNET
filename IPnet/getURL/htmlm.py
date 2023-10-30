# 接着utlm流程，获取文本
import urllib3
import threading
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import gethtml
from concurrent.futures import as_completed
import validators
import warnings

warnings.filterwarnings("ignore")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# total_searches = 0  # 总搜索次数
# empty_searches = 0  # 搜索结果为空次数
# total_html_fetches = 0  # 总获取网页次数
# empty_html_fetches = 0  # 获取网页结果为空次数


# 创建日志输出函数
def log_to_file(msg):
    # 使用当前线程id作为日志文件名
    thread_id = threading.get_ident()
    with open(f"D:/DoAc/trainset/logs/log{thread_id}.txt", 'a') as file:
        file.write(msg + '\n')
    # print(msg)


def worker(item):
    try:
        # 从item中提取信息
        ipv6 = item["ipv6"]
        urls = item["urls"]

        # 获取文本
        unique_urls = set(urls)  # 转换为集合，去除重复项
        texts = []
        for url in unique_urls:
            if validators.url(url):  # 判断URL是否有效
                text = gethtml.get_web_text(url)
                if text is not None:
                    texts.append(text)
        if not texts:
            return
        combined_text = " ".join(texts)
        # 获取组织名
        org_name = gethtml.get_certificate_organization(urls[0]) if urls else None
        if org_name:
            org_name = org_name.replace('"', '').replace("'", '')
        datalist = [ipv6, list(unique_urls), org_name, combined_text]
        if org_name:
            with open("D:/DoAc/trainset/final_set.txt", "a", encoding="utf-8") as file:
                file.write(str(datalist) + "\n")
        else:
            with open("D:/DoAc/trainset/noorg_set.txt", "a", encoding="utf-8") as file:
                file.write(str(datalist) + "\n")

    except Exception as e:
        log_to_file(f"处理记录 {item} 时发生错误: {str(e)}")


def main():
    # global total_searches, empty_searches, total_html_fetches, empty_html_fetches
    data = gethtml.load_and_process_data('D:/DoAc/trainset/query_url4.txt')
    with ThreadPoolExecutor(max_workers=30) as executor:
        # 创建一个 future 对象的列表，每个 future 对象代表一个尚未完成的计算
        futures = [executor.submit(worker, item) for item in data]
        # 创建一个进度条
        progress_bar = tqdm(total=len(futures), desc="处理进度")
        for future in as_completed(futures):
            # 进度条每次更新一个
            progress_bar.update(1)
        progress_bar.close()


if __name__ == "__main__":
    main()
