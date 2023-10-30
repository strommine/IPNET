# 最初的获取url和文本的全过程，分开存储html--弃用
import os
import json
import urllib3
import threading
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import ptr_sel
import searcher
import gethtml
from concurrent.futures import as_completed
import warnings

warnings.filterwarnings("ignore")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

total_searches = 0  # 总的搜索次数
empty_searches = 0  # 搜索结果为空的次数
total_html_fetches = 0  # 总的获取网页的次数
empty_html_fetches = 0  # 获取网页结果为空的次数


# 创建日志输出函数，将日志信息写入对应的文件
def log_to_file(msg):
    # 使用当前线程id作为日志文件名的一部分
    thread_id = threading.get_ident()
    with open(f"D:/DoAc/trainset/logs/log{thread_id}.txt", 'a') as file:
        file.write(msg + '\n')
    # print(msg)  # 打印到控制台


# 修改 worker 函数，使用日志输出函数替换 print 函数

def worker(item):
    global total_searches, empty_searches, total_html_fetches, empty_html_fetches
    try:
        ipv6, query = ptr_sel.process_ptr_record(item)
        log_to_file(f"正在搜索: {ipv6}, 查询: {query}")
        search_results = searcher.perform_search(query)
        total_searches += 1
        if not search_results:
            empty_searches += 1
            # 如果搜索结果为空，直接跳到下一个项目
            return
        top_results = gethtml.preprocess_urls(query, search_results)
        result_dict = {
            "ipv6": ipv6,
            "query": query,
            "urls": top_results
        }
        total_html_fetches += 1
        with open("D:/DoAc/trainset/query_url.txt", 'a') as outfile:
            json.dump(result_dict, outfile)
            outfile.write("\n")
        filename = ipv6.replace(':', '_') + '.json'
        web_texts = []
        for url in top_results:
            web_text = gethtml.get_web_text(url)
            if web_text:
                web_texts.append((url, web_text))
        if not web_texts:
            empty_html_fetches += 1
            error_record = {
                "ipv6": ipv6,
                "ptr": list(item.values())[0],
                "query": query,
                "urls": top_results
            }
            with open("D:/DoAc/trainset/error_url.txt", 'a') as errorfile:
                json.dump(error_record, errorfile)
                errorfile.write("\n")
                return
        with open(os.path.join("D:/DoAc/trainset/htmls/", filename), 'w') as file:
            for url, web_text in web_texts:
                json.dump({url: web_text}, file)
                file.write("\n")
    except Exception as e:
        log_to_file(f"处理记录 {item} 时发生错误: {str(e)}")


def main():
    global total_searches, empty_searches, total_html_fetches, empty_html_fetches
    data = ptr_sel.load_and_process_data('D:/DoAc/trainset/div-ptr-nn.txt')
    with ThreadPoolExecutor(max_workers=30) as executor:
        # 创建一个 future 对象的列表，每个 future 对象代表一个尚未完成的计算
        futures = [executor.submit(worker, item) for item in data]
        # 创建一个进度条
        progress_bar = tqdm(total=len(futures), desc="处理进度")
        for future in as_completed(futures):
            # 进度条每次更新一个
            progress_bar.update(1)
        progress_bar.close()
        empty_search_ratio = empty_searches / total_searches
        empty_html_fetch_ratio = empty_html_fetches / total_html_fetches
        print(f"空url列表: {empty_search_ratio * 100:.2f}%")
        print(f"空html列表: {empty_html_fetch_ratio * 100:.2f}%")


if __name__ == "__main__":
    main()
