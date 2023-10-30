#移除none--弃用

import json
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

# 定义一个处理单行数据的函数
def process_line(line):
    parsed_line = json.loads(line)
    if list(parsed_line.values())[0] is not None:
        return line

def main():
    # 读取源文件
    with open('D:/DoAc/div-ptr.txt', 'r') as source_file:
        lines = source_file.readlines()

    # 创建一个进程池，使用所有可用的处理器
    with Pool(cpu_count()) as pool:
        # 使用tqdm显示进度条
        results = list(tqdm(pool.imap(process_line, lines), total=len(lines)))

    # 移除值为None的行
    valid_lines = [line for line in results if line is not None]

    # 写入目标文件
    with open('D:/DoAc/div-ptr-nn.txt', 'w') as target_file:
        target_file.writelines(valid_lines)

if __name__ == "__main__":
    main()
