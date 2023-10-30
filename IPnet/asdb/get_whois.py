from threading import Thread, Lock
from queue import Queue
import re
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from tqdm import tqdm

# 创建一个锁对象来保护对进度条的更新
progress_lock = Lock()
progress_bar = None

def fetch_query_results(queue, output_file_path):
    global progress_bar
    # 创建一个Options对象来存储webdriver的选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    # 创建一个Service对象
    service = Service(executable_path='D:\\WebDownload\\chromedriver.exe')

    # 使用配置好的选项和服务来初始化webdriver
    driver = webdriver.Chrome(options=chrome_options, service=service)
    while True:
        line_data = queue.get()
        if line_data is None:
            break

        query, second_field = line_data

        try:
            # 设置超时时间
            driver.set_page_load_timeout(100)
            driver.set_script_timeout(100)

            # Construct the URL from the query parameter
            url = f"https://wq.apnic.net/static/search.html?query={query}"

            # 打开网页
            driver.get(url)

            # print("Waiting for the content to load...")
            time.sleep(8)

            # print("Parsing the HTML content...")
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')

            query_results = soup.find(id='query-results')
            if not query_results:
                driver.quit()
                return "Element with id='query-results' not found."

            # print("Extracting text from nested divs...")
            object_divs = query_results.find_all('div', class_='object')
            div_texts = [div.find('pre').get_text('#') for div in object_divs if div.find('pre')]

            # 将所有文本内容合并为一个字符串
            result_text = "\n".join(div_texts)

            # Using a regular expression to find and extract the desired string
            abuse_contact_info = re.search(r"% Abuse contact for 'AS\d+' is '(.+?)'", result_text)

            if abuse_contact_info:
                email_domains = [abuse_contact_info.group(1).split('@')[1]]  # 获取电子邮件域名部分
            else:
                # 如果第一个正则表达式没有找到匹配项，尝试使用第二个正则表达式查找电子邮件
                org_abuse_emails = re.findall(r'AbuseEmail:#(.+?@.+?)#', result_text)
                if org_abuse_emails:
                    email_domains = [email.split('@')[1] for email in org_abuse_emails]  # 获取所有电子邮件的域名部分
                else:
                    org_abuse_emails = re.findall(r'e-mail:#(.+?@.+?)#', result_text)
                    if org_abuse_emails:
                        email_domains = [email.split('@')[1] for email in org_abuse_emails]  # 获取所有电子邮件的域名部分
                    else:
                        email_domains = ['']  # 如果都没有找到，则返回空列表

            # 如果找到电子邮件域名，将其添加到line_data列表中并写入输出文件
            if email_domains:
                email_domains = list(set(email_domains))
                line_data.append(email_domains)
                with open(output_file_path, 'a') as outfile:
                    outfile.write(str(line_data) + '\n')

        except Exception as e:
            email_domains = ['']
            line_data.append(email_domains)
            with open(output_file_path, 'a') as outfile:
                outfile.write(str(line_data) + '\n')
            if driver:
                driver.quit()

        finally:
            with progress_lock:
                progress_bar.update(1)

        queue.task_done()


def main():
    global progress_bar
    input_file_path = 'D:\\DoAc\\asdb\\Gold\\isp-asn.txt'
    output_file_path = 'D:\\DoAc\\asdb\\Gold\\have-whois.txt'

    total_tasks = sum(1 for _ in open(input_file_path))
    progress_bar = tqdm(total=total_tasks, dynamic_ncols=True)

    queue = Queue()

    # 创建线程池
    for i in range(10):
        worker = Thread(target=fetch_query_results, args=(queue, output_file_path))
        worker.daemon = True
        worker.start()

    with open(input_file_path, 'r') as infile:
        for line in infile:
            line_data = eval(line.strip())
            queue.put(line_data)

    queue.join()
    progress_bar.close()


if __name__ == "__main__":
    main()
