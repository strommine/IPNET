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

# 配置Chrome选项
chrome_options = Options()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')

# 创建一个Service对象
service = Service(executable_path='D:\\WebDownload\\chromedriver.exe')

# 初始化线程本地数据
thread_local = threading.local()


def get_driver():
    if not hasattr(thread_local, "driver"):
        thread_local.driver = webdriver.Chrome(options=chrome_options, service=service)
        thread_local.driver.set_page_load_timeout(30)  # 设置页面加载超时时间为30秒
    return thread_local.driver


def fetch_data(ipv6):
    ipv6 = ipv6.strip()
    url = f"https://wq.apnic.net/static/search.html?query={ipv6}"

    while True:
        try:
            driver = get_driver()
            driver.get(url)
            # 等待内容加载（根据需要调整时间）
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'pre')))

            # 获取页面源代码并用BeautifulSoup解析
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # 提取所需数据
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
                return ipv6, nested_table_data
            else:
                with open('D:/DoAc/whois/error.txt', 'a') as error_file:
                    error_file.write(f"{ipv6}\n")
                time.sleep(10)  # 如果数据是空列表，等待10秒后再次尝试
        except Exception as e:
            with open('D:/DoAc/whois/error.txt', 'a') as error_file:
                error_file.write(f"{ipv6}\n")
            time.sleep(10)  # 出现异常时，等待10秒后再次尝试


def main():
    # 从文件中读取IPv6地址
    with open('D:/DoAc/whois/ipv6.txt', 'r') as f:
        ipv6_addresses = f.readlines()

    results = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_ipv6 = {executor.submit(fetch_data, ipv6): ipv6 for ipv6 in ipv6_addresses}
        for future in as_completed(future_to_ipv6):
            ipv6, data = future.result()
            if data is not None:  # 只有当数据部分不是None时，才将其添加到结果集
                results[ipv6] = data
                # print(ipv6)
                # print(data)

    # 保存结果到文件
    with open('D:/DoAc/whois/out.txt', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    # 关闭驱动程序
    if hasattr(thread_local, "driver"):
        thread_local.driver.quit()


if __name__ == "__main__":
    main()
