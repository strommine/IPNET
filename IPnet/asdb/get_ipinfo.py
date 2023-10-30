from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import local
import time

thread_local = local()


def login_to_ipinfo(username, password):
    # 设置Chrome选项以在后台运行
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('headless')

    # 初始化webdriver
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 打开登录页面
        driver.get("https://ipinfo.io/login")

        # 等待登录页面加载完成
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'email')))

        # 找到用户名和密码输入框并输入相应的信息
        email_input = driver.find_element(By.NAME, "email")
        password_input = driver.find_element(By.NAME, "password")
        email_input.send_keys(username)
        password_input.send_keys(password)

        # 找到并点击登录按钮
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()

        # 等待登录完成
        time.sleep(5)

        # 导航到搜索页面
        driver.get("https://ipinfo.io/account/search")

        # 等待网页加载完成
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, 'query')))

        return driver
    except Exception as e:
        print(f"Error during login: {e}")
        driver.quit()


def get_as_info(driver, as_number):
    try:
        # 找到搜索框并输入AS号
        search_box = driver.find_element(By.NAME, "query")
        search_box.clear()
        search_box.send_keys(as_number)

        time.sleep(10)

        dl_tag = driver.find_element(By.TAG_NAME, 'dl')
        dt_tags = dl_tag.find_elements(By.TAG_NAME, 'dt')
        dd_tags = dl_tag.find_elements(By.TAG_NAME, 'dd')

        # 提取和存储结果
        result_dict = {}
        for dt, dd in zip(dt_tags, dd_tags):
            result_dict[dt.text] = dd.text

        # 获取Domain值并去掉内层的双引号
        domain_value = result_dict.get('domain', 'domain not found').replace('"', '')
        return domain_value
    except Exception as e:
        print(f"Error during information retrieval: {e}")


def get_driver():
    # 如果当前线程还没有driver实例，就创建一个
    if not hasattr(thread_local, "driver"):
        thread_local.driver = login_to_ipinfo('ykez666@qq.com', 'txWFJ9*sDrrJs$k')
    return thread_local.driver


# 定义一个函数来处理每一行的数据
def process_line(line):
    driver = get_driver()
    as_info_list = eval(line.strip())

    # 获取AS号
    as_number = as_info_list[0]
    domain_value = get_as_info(driver, as_number)

    # result_list = [as_info_list[0], as_info_list[1], [as_info_list[2], domain_value]]
    as_info_list[-1].append(domain_value)

    # 将结果追加到文件
    with open('D:\\DoAc\\asdb\\Gold\\ipinfo2.txt', 'a') as f:
        f.write(str(as_info_list) + '\n')

    pbar.update(1)


with open('D:\\DoAc\\asdb\\Gold\\missing_asn_list.txt', 'r') as f:
    lines = f.readlines()


# 创建一个线程池
with ThreadPoolExecutor(max_workers=5) as executor:
    # 创建进度条
    with tqdm(total=len(lines)) as pbar:
        # 创建一个列表来存储Future对象
        futures = [executor.submit(process_line, line) for line in lines]

        # 迭代完成的Future对象
        for future in as_completed(futures):
            # 更新进度条
            pbar.update(1)

# 关闭所有的driver实例
if hasattr(thread_local, "driver"):
    thread_local.driver.quit()




