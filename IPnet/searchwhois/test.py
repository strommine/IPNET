import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from tqdm import tqdm

# 配置Chrome选项
chrome_options = Options()
chrome_options.add_argument('--headless')
# chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')

# 创建一个Service对象
service = Service(executable_path='D:\\WebDownload\\chromedriver.exe')

# 初始化线程本地数据
thread_local = threading.local()

# 创建一个锁和结果列表
results_lock = threading.Lock()
results = []

# 定义一个用于写入文件的函数
def write_to_file(data_list):
    with open('D:/DoAc/whois/out.txt', 'a', encoding='utf-8') as f:
        for item in data_list:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')


def get_driver():
    if not hasattr(thread_local, "driver"):
        thread_local.driver = webdriver.Chrome(options=chrome_options, service=service)
        thread_local.driver.set_page_load_timeout(30)  # 设置页面加载超时时间为30秒
    return thread_local.driver


def fetch_data(ipv6):
    global results
    ipv6 = ipv6.strip()
    url = f"https://wq.apnic.net/static/search.html?query={ipv6}"

    max_retries = 3  # 设置最大重试次数
    attempt = 0  # 初始化尝试次数

    while attempt < max_retries:
        try:
            driver = get_driver()
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'pre')))

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            nested_table_data = []
            pre_tags = soup.find_all('pre')
            for pre_tag in pre_tags:
                tables_in_pre = pre_tag.find_all('table')
                for table in tables_in_pre:
                    table_data = {}
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) == 2:
                            key = cells[0].get_text(strip=True)
                            value = cells[1].get_text(strip=True)
                            table_data[key] = value
                    if table_data:
                        nested_table_data.append(table_data)

            if nested_table_data:
                with results_lock:
                    results.append({ipv6: nested_table_data})
                    if len(results) >= 10:
                        write_to_file(results)
                        results = []
                return
            else:
                attempt += 1  # 增加尝试次数
                if attempt < max_retries:
                    time.sleep(1)  # 如果未达到最大重试次数，则等待30秒再尝试
                else:
                    with open('D:/DoAc/whois/error.txt', 'a') as error_file:
                        error_file.write(f"{ipv6}\n")
        except Exception as e:
            # print(e)
            attempt += 1  # 增加尝试次数
            if attempt < max_retries:
                time.sleep(1)  # 如果未达到最大重试次数，则等待10秒再尝试
            else:
                with open('D:/DoAc/whois/error.txt', 'a') as error_file:
                    error_file.write(f"{ipv6}\n")


def main():
    # 从文件中读取IPv6地址
    with open('D:/DoAc/whois/ipasn.txt', 'r') as f:
        ipv6_addresses = f.readlines()

    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_ipv6 = {executor.submit(fetch_data, ipv6): ipv6 for ipv6 in ipv6_addresses}
        for future in tqdm(as_completed(future_to_ipv6), total=len(ipv6_addresses), desc='Fetching data', unit='IP'):
            pass

    # 将剩余的结果写入文件
    with results_lock:
        if results:
            write_to_file(results)

    # 关闭驱动程序
    if hasattr(thread_local, "driver"):
        thread_local.driver.quit()


if __name__ == "__main__":
    main()
