import time
from selenium.webdriver.common.keys import Keys
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
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')

# 创建一个Service对象
service = Service(executable_path='D:\\WebDownload\\chromedriver.exe')

# 初始化线程本地数据
thread_local = threading.local()


def get_driver():
    if not hasattr(thread_local, "driver"):
        while True:
            try:
                thread_local.driver = webdriver.Chrome(options=chrome_options, service=service)
                thread_local.driver.set_page_load_timeout(30)  # 设置页面加载超时时间为30秒
                thread_local.driver.get("https://wq.apnic.net/static/search.html")
                break
            except:
                thread_local.driver.quit()
                time.sleep(5)  # 重试之前稍作等待
    return thread_local.driver



def fetch_data(ipv6):
    time.sleep(1)
    driver = get_driver()
    ipv6 = ipv6.strip()

    try:
        # 通过其name或id找到搜索框，并输入IPv6地址
        search_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, 'searchtext'))
        )

        # 使用CTRL+A和BACKSPACE来清除搜索框的内容
        search_box.send_keys(Keys.CONTROL + "a")
        search_box.send_keys(Keys.BACKSPACE)

        # 输入新的IPv6地址
        search_box.send_keys(ipv6)

        # 提交表单来触发搜索
        search_box.submit()

        # 等待内容加载（根据需要调整时间）
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'pre')))

        # 获取页面源代码并用BeautifulSoup解析
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 像之前一样找到并提取所需数据
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

        if not nested_table_data:  # 如果返回的数据是空列表
            time.sleep(10)  # 等待10秒后重新查询
            return fetch_data(ipv6)

        return ipv6, nested_table_data

    except Exception as e:
        with open('D:/DoAc/whois/error.txt', 'a') as error_file:
            error_file.write(f"{ipv6}\n")
        return ipv6, None


def main():
    # 从文件中读取IPv6地址
    with open('D:/DoAc/whois/ipv6.txt', 'r') as f:
        ipv6_addresses = f.readlines()

    results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_ipv6 = {executor.submit(fetch_data, ipv6): ipv6 for ipv6 in ipv6_addresses}
        for future in tqdm(as_completed(future_to_ipv6), total=len(ipv6_addresses), unit="task"):  # 修改这行
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