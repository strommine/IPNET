from selenium import webdriver

# def query_apnic_asn(as_number):
#     driver = None
#     try:
#         options = webdriver.ChromeOptions()
#         options.add_argument('--headless')
#         driver = webdriver.Chrome('D:\\WebDownload\\chromedriver.exe', options=options)
#         driver.get(f'https://wq.apnic.net/static/search.html?query={as_number}')
#         driver.implicitly_wait(20)  # 设置一个20秒的等待时间
#         result_div = driver.find_element_by_id('query-results')
#         if result_div:
#             text_content = result_div.text
#             return text_content
#         else:
#             print(f"No data found for {as_number}")
#             return None
#     except Exception as e:
#         print(f"Error querying {as_number}: {e}")
#         return None
#     finally:
#         if driver:
#             driver.quit()
#
# # 测试代码
# as_number = "AS6781"
# response = query_apnic_asn(as_number)
# print(response)


# from selenium import webdriver
# from bs4 import BeautifulSoup
# import time
# import re
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
#
# def fetch_query_results(url):
#     driver = None  # 初始化driver变量以避免引用前未赋值的错误
#     try:
#         print("Opening the webpage using a web driver...")
#
#         # 创建一个Options对象来存储webdriver的选项
#         chrome_options = Options()
#         chrome_options.add_argument('--headless')  # 使用无头模式
#         chrome_options.add_argument('--disable-gpu')  # 禁用GPU加速
#         chrome_options.add_argument('--no-sandbox')  # 禁用沙箱模式
#
#         # 创建一个Service对象
#         service = Service(executable_path='D:\\WebDownload\\chromedriver.exe')
#
#         # 使用配置好的选项和服务来初始化webdriver
#         driver = webdriver.Chrome(options=chrome_options, service=service)
#
#         # 打开网页
#         driver.get(url)
#
#         print("Waiting for the content to load...")
#
#         # 等待页面上的动态内容加载完成（您可以根据需要调整等待时间）
#         time.sleep(10)
#
#         print("Parsing the HTML content...")
#
#         # 获取网页的HTML内容
#         html_content = driver.page_source
#
#         # 解析HTML内容
#         soup = BeautifulSoup(html_content, 'html.parser')
#
#         # 输出HTML的前500个字符以检查其内容
#         # print(f"HTML Content (first 500 chars): {soup.prettify()[:500]}")
#
#         # 查找id='query-results'的元素
#         query_results = soup.find(id='query-results')
#         if not query_results:
#             driver.quit()
#             return "Element with id='query-results' not found."
#
#         print("Extracting text from nested divs...")
#
#         # 查找所有class='object'的div元素并提取文本内容
#         object_divs = query_results.find_all('div', class_='object')
#         div_texts = [div.find('pre').get_text() for div in object_divs if div.find('pre')]
#
#         # 将所有文本内容合并为一个字符串
#         result_text = "\n".join(div_texts)
#
#         # 使用正则表达式找到和提取所需的字符串
#         abuse_contact_info = re.search(r"% Abuse contact for 'AS2834' is '(.+?)'", result_text)
#         if abuse_contact_info:
#             result_text = abuse_contact_info.group(0)  # 获取匹配到的整个字符串
#         else:
#             result_text = "Abuse contact information not found."
#
#         print("Extraction completed. Here is the result:")
#         print(result_text)  # 打印结果字符串
#
#         # 关闭web driver
#         driver.quit()
#
#         return result_text
#     except Exception as e:
#         if driver:  # 在尝试关闭driver之前检查它是否已被初始化
#             driver.quit()
#         return str(e)
#
# # 使用函数
# url = "https://wq.apnic.net/static/search.html?query=AS2834"
# result_text = fetch_query_results(url)
# print(result_text)  # 打印结果文本的前500个字符

import re
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from threading import Thread
from queue import Queue
import re
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def fetch_query_results(queue, output_file_path):
    while True:
        line_data = queue.get()
        if line_data is None:
            break

        query, second_field = line_data
        driver = None
        try:
            print(f"Opening the webpage using a web driver for query {query}...")

            url = f"https://wq.apnic.net/static/search.html?query={query}"

            # 创建一个Options存储webdriver的选项
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')

            # 创建一个Service对象
            service = Service(executable_path='D:\\WebDownload\\chromedriver.exe')

            # 使用配置好的选项和服务来初始化webdriver
            driver = webdriver.Chrome(options=chrome_options, service=service)

            # 打开网页
            driver.get(url)

            print("Waiting for the content to load...")
            time.sleep(10)

            print("Parsing the HTML content...")
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')

            query_results = soup.find(id='query-results')
            if not query_results:
                driver.quit()
                return "Element with id='query-results' not found."

            print("Extracting text from nested divs...")
            object_divs = query_results.find_all('div', class_='object')
            div_texts = [div.find('pre').get_text() for div in object_divs if div.find('pre')]

            # 将所有文本内容合并为一个字符串
            result_text = "\n".join(div_texts)

            abuse_contact_info = re.search(r"% Abuse contact for 'AS\d+' is '(.+?)'", result_text)
            if abuse_contact_info:
                result_text = abuse_contact_info.group(1)  # Getting the email address part
                line_data.append(result_text)
                with open(output_file_path, 'a') as outfile:
                    outfile.write(str(line_data)+'\n')

        except Exception as e:
            if driver:
                driver.quit()

        queue.task_done()


def main():
    input_file_path = 'D:\\DoAc\\asdb\\test.txt'
    output_file_path = 'D:\\DoAc\\asdb\\mail.txt'

    queue = Queue()

    for i in range(20):
        worker = Thread(target=fetch_query_results, args=(queue, output_file_path))
        worker.daemon = True
        worker.start()

    with open(input_file_path, 'r') as infile:
        for line in infile:
            line_data = eval(line.strip())
            queue.put(line_data)

    queue.join()


if __name__ == "__main__":
    main()




