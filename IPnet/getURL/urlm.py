# 获取url和其内页url
import json
import urllib3
import threading
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import ptr_sel
from searcher import *
from concurrent.futures import as_completed
import warnings

warnings.filterwarnings("ignore")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

total_searches = 0  # 总的搜索次数
empty_searches = 0  # 搜索结果为空的次数
total_html_fetches = 0  # 总的获取网页的次数
empty_html_fetches = 0  # 获取网页结果为空的次数


# # 创建日志输出函数，将日志信息写入对应的文件
# def log_to_file(msg):
#     # 使用当前线程id作为日志文件名的一部分
#     thread_id = threading.get_ident()
#     with open(f"D:/DoAc/real/logs/log{thread_id}.txt", 'a') as file:
#         file.write(msg + '\n')
#     # print(msg)  # 打印到控制台


def worker(item):
    global total_searches, empty_searches, total_html_fetches, empty_html_fetches
    try:
        ipv6, query = ptr_sel.process_ptr_record(item)
        log_to_file(f"正在搜索: {ipv6}, 查询: {query}")
        search_results = perform_search(query)
        total_searches += 1
        if not search_results:
            empty_searches += 1
            # 如果搜索结果为空，跳到下一个项目
            log_to_file(f"搜索结果为空 {ipv6}  {query}")
            return
        top_results = preprocess_urls(search_results)
        result_dict = {
            "ipv6": ipv6,
            "query": query,
            "urls": top_results
        }
        total_html_fetches += 1
        with open("D:/DoAc/real/query_url.txt", 'a') as outfile:
            json.dump(result_dict, outfile)
            outfile.write("\n")
    except Exception as e:
        log_to_file(f"处理记录 {item} 时发生错误: {str(e)}")


def main():
    global total_searches, empty_searches, total_html_fetches, empty_html_fetches
    data = ptr_sel.load_and_process_data('D:/DoAc/real/div-ptr-nnc.txt')
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker, item) for item in data]
        # 创建进度条
        progress_bar = tqdm(total=len(futures), desc="处理进度")
        for future in as_completed(futures):
            progress_bar.update(1)
        progress_bar.close()
        empty_search_ratio = empty_searches / total_searches
        print(f"空url列表: {empty_search_ratio * 100:.2f}%")


if __name__ == "__main__":
    main()
