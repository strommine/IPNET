#ptr去重

import json

def extract_field(domain):
    parts = domain.split('.')
    # 如果域名分割后的记录数超过1，则返回最后两个字段，否则返回最后一个字段。
    return (parts[-3], parts[-2]) if len(parts) > 2 else (None, parts[-2])


# 文件路径
input_file_path = "D:\\DoAc\\real\\allptr.txt"
output_file_path = "D:\\DoAc\\real\\div-ptr-nnc.txt"

seen_fields = set()  # 用于存储已经看到的字段对
results = []  # 用于存储结果

# 打开并读取文件
with open(input_file_path, 'r') as file:
    for line in file:
        data = json.loads(line.strip())
        for ip, domain in data.items():
            field = extract_field(domain)
            if field not in seen_fields:
                results.append(data)
                seen_fields.add(field)

# 将结果保存到另一个文件中
with open(output_file_path, 'w') as output_file:
    for res in results:
        output_file.write(json.dumps(res) + '\n')
