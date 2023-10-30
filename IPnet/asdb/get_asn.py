import csv
import random

# 打开csv文件进行读取
with open('D:\\DoAc\\asdb\\2023-05_categorized_ases.csv', 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.reader(csv_file)

    # 创建两个列表分别存储标记为'1'和'0'的行
    rows_with_1 = []
    rows_with_0 = []

    for row in csv_reader:
        try:
            # 根据条件将行添加到相应的列表
            if 'Internet Service Provider (ISP)' in row[1:9]:
                rows_with_1.append(f"['{row[0]}', '1']")
            else:
                rows_with_0.append(f"['{row[0]}', '0']")
        except IndexError as e:
            print(f"Encountered an error on row {csv_reader.line_num}: {e}")

# 从每个列表中随机选取75个条目
selected_rows_with_1 = random.sample(rows_with_1, 75)
selected_rows_with_0 = random.sample(rows_with_0, 75)

# 合并选定的行并随机排列
selected_rows = selected_rows_with_1 + selected_rows_with_0
random.shuffle(selected_rows)

# 打开或创建txt文件进行写入
with open('D:\\DoAc\\asdb\\Gold\\isp-asn.txt', 'w', encoding='utf-8') as txt_file:
    for row in selected_rows:
        txt_file.write(row + '\n')
