import json
from collections import Counter

# 过滤1: 创建一个包含全球最常见的10个邮箱域名的列表
common_domains = [
    "gmail.com", "yahoo.com", "outlook.com",
    "icloud.com", "aol.com", "zoho.com", "mail.com",
    "yandex.com", "protonmail.com", "gmx.com"
]

# 读取文件，并创建一个列表来存储每行的数据
with open('D:\\DoAc\\asdb\\Gold\\have-whois-ipinfo-peeringdb.txt', 'r') as file:
    lines = file.readlines()

# 对每行数据进行处理，先执行过滤1
data_list = []
for line in lines:
    data = eval(line.strip())
    domain_list = data[2]
    for domain in domain_list:
        if len(domain_list) > 1:
            if domain in common_domains:
                domain_list.remove(domain)
    data[2] = domain_list
    data_list.append(data)


# 过滤2: 在执行过滤2之前，我们需要先统计每个域名的出现次数
all_domains = [domain for data in data_list for domain in data[2]]
domain_counts = Counter(all_domains)

# 执行过滤2，剔除出现次数超过100次的域名
for data in data_list:
    domain_list = data[2]
    for domain in domain_list:
        if len(domain_list) > 1:
            if domain_counts[domain] > 100:
                domain_list.remove(domain)
        data[2] = domain_list

# 将处理后的数据保存到一个新文件中
with open('D:\\DoAc\\asdb\\Gold\\filter2.txt', 'w') as output_file:
    for data in data_list:
        output_file.write(str(data) + '\n')
