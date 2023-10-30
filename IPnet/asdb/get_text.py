import requests
from bs4 import BeautifulSoup
from langdetect import detect
from googletrans import Translator
import string


def process_line(line):
    try:
        # 解析行数据
        data = eval(line)
        as_number, char, urls = data[0], data[1], data[2]
        data = [as_number, char, urls]

        # 初始化翻译器
        translator = Translator()

        # 初始化一个空字符串来保存所有网站的文本
        total_text = ""

        # 用于跟踪是否有至少一个URL成功
        success_flag = False

        for url in urls:
            try:
                # 为根域名添加协议前缀
                if not url.startswith('http'):
                    url = 'https://' + url

                # 获取网页内容
                response = requests.get(url)
                response.raise_for_status()

                # 使用BeautifulSoup解析网页内容
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()

                # 检测文本语言并翻译成英文（如果需要）
                lang = detect(text)
                if lang != 'en':
                    text = translator.translate(text, dest='en').text

                # 清理文本
                text = ''.join(
                    [char if char in string.ascii_letters or char.isdigit() or char.isspace() else ' ' for char in
                     text])
                text = ' '.join(text.split())  # 处理多余的空格和空行

                # 添加到总文本
                total_text += text + " "

                # URL成功
                success_flag = True

            except Exception as e:
                # 如果URL失败，记录错误并继续处理下一个URL
                total_text += f"Error processing URL {url}: {str(e)} "

        # 将获取到的文本添加到原始数据列表中
        data.append(total_text.strip())

        # 根据success_flag返回成功或失败的结果
        if success_flag:
            return ('success', str(data))
        else:
            return ('failure', str(data))

    except Exception as e:
        # 返回失败的结果和错误信息
        return ('failure', str(data.append(str(e))))


def main(input_file, output_file, error_file):
    with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'a', encoding='utf-8') as f_out, open(error_file, 'a', encoding='utf-8') as f_err:
        lines = f_in.readlines()
        total_lines = len(lines)

        for i, line in enumerate(lines):
            status, result = process_line(line)
            if status == 'success':
                f_out.write(result + '\n')
            else:
                f_err.write(result + '\n')

            # 输出进度信息
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{total_lines} lines.")


# 调用主函数
main('D:/DoAc/asdb/Gold/error4.txt', 'D:/DoAc/asdb/Gold/success5.txt', 'D:/DoAc/asdb/Gold/error5.txt')
