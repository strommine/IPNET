import json
from ast import literal_eval

# 步骤1: 读取JSON文件并创建一个字典来存储AS号和对应的website
from urllib.parse import urlparse

with open('D:\\DoAc\\asdb\\peeringdb.josn', 'r') as f:
    data = json.load(f)['data']

asn_to_website = {str(item['asn']): item['website'] for item in data if 'asn' in item and 'website' in item}

# 步骤2: 读取之前筛选出的150条记录的文件
with open('D:\\DoAc\\asdb\\Gold\\have-whois-ipinfo.txt', 'r') as f:
    records = [literal_eval(line.strip()) for line in f.readlines()]

# 步骤3: 更新记录，添加website字段
for record in records:
    asn = record[0][2:]
    sublist = record[2]
    if 'null' in sublist:
        sublist.remove('null')
    if asn in asn_to_website and asn_to_website[asn] and asn_to_website[asn] != 'null':
        sublist.append(urlparse(asn_to_website[asn]).netloc.replace('www.', ''))
    record[2] = list(set(sublist))

# 步骤4: 将更新后的记录保存到新的目标文件
with open('D:\\DoAc\\asdb\\Gold\\have-whois-ipinfo-peeringdb.txt', 'w') as f:
    for record in records:
        f.write(str(record) + '\n')
