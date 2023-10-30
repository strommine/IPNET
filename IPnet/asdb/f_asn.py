from ast import literal_eval
import json
import random

# 步骤1: 读取文件，并尝试使用literal_eval解析每一行为Python列表
file_path = 'D:\\DoAc\\asdb\\mail.txt'  # 请替换为您的文件路径
all_records = []

with open(file_path, 'r') as f:
    lines = f.readlines()

for line in lines:
    try:
        record = literal_eval(line.strip())
        all_records.append(record)
    except:
        pass

# 步骤2: 分别提取标记为'0'和'1'的记录，并保证子列表不重复
records_0 = []
records_1 = []
seen_sublists = set()
random.shuffle(all_records)

for record in all_records:
    sublist = json.dumps(record[2])
    if sublist not in seen_sublists:
        if record[1] == '0' and len(records_0) < 75:
            records_0.append(record)
            seen_sublists.add(sublist)
        elif record[1] == '1' and len(records_1) < 75:
            records_1.append(record)
            seen_sublists.add(sublist)

        if len(records_0) >= 75 and len(records_1) >= 75:
            break

# 步骤3: 混洗并保存选定的记录到目标文件
output_records = records_0 + records_1
random.shuffle(output_records)

output_path = 'D:\\DoAc\\asdb\\gold2.txt'  # 请替换为您想要保存的文件路径
with open(output_path, 'w') as f:
    for record in output_records:
        f.write(json.dumps(record) + '\n')
