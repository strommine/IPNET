# 处理数据用
# 删除出现次数最多的公司

from collections import Counter

# 1. 读取文件并提取公司名
with open("D:\\DoAc\\roothtml\\results.txt", "r", encoding="ISO-8859-1") as f:
    lines = f.readlines()

organizations = [line.split('", "')[1].replace('"]\n', '') for line in lines]
org_count = Counter(organizations)

# 2. 确定出现次数最多的前10个公司
top_10_orgs = org_count.most_common(10)
print("Top 10 organizations and their counts:")
for org, count in top_10_orgs:
    print(f"{org}: {count}")

# 3. 删除出现次数最多的公司的记录
most_common_org = top_10_orgs[0][0]
filtered_lines = [line for line in lines if most_common_org not in line]

# 4. 将过滤后的结果写回到新的文件中
with open("D:\\DoAc\\roothtml\\results_filtered.txt", "w", encoding="ISO-8859-1") as f:
    f.writelines(filtered_lines)
