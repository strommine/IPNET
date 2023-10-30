import ast
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib

matplotlib.use('TkAgg')


def analyze_categories(filepath):
    labels = []

    # 从文件中读取标签
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = ast.literal_eval(line.strip())
                if len(data) >= 4:
                    labels.append(data[2])
            except SyntaxError as e:
                print(f"Skipping line due to SyntaxError: {e}")
                continue

    # 统计标签出现的次数
    label_counter = Counter(labels)

    # 使用pandas的DataFrame来显示标签和相应的出现次数
    df = pd.DataFrame(list(label_counter.items()), columns=["Label", "Frequency"])

    # 将DataFrame按"Frequency"列逆序排列
    df = df.sort_values(by='Frequency', ascending=False)
    print(df)  # 打印表格形式的数据

    # 可视化
    labels, frequencies = zip(*df.values)
    plt.figure(figsize=(12, 8))
    plt.barh(labels[::-1], frequencies[::-1])  # 使用[::-1]来逆序
    plt.xlabel('Frequency')
    plt.ylabel('Labels')
    plt.title('Distribution of Labels')
    plt.show()


if __name__ == "__main__":
    filepath = "D:/DoAc/trainset/g-final-set-100.txt"
    analyze_categories(filepath)
