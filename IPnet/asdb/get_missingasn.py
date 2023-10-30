from pathlib import Path

# 读取文件内容
have_whois_content = Path('/mnt/data/have-whois.txt').read_text()
have_whois_ipinfo_content = Path('/mnt/data/have-whois-ipinfo.txt').read_text()

# 将每一行转换为列表，并提取AS号和完整列表
have_whois_dict = {line.split()[0]: line for line in have_whois_content.split('\n') if line}
have_whois_ipinfo_dict = {line.split()[0]: line for line in have_whois_ipinfo_content.split('\n') if line}

# 查找在第一个文件中但不在第二个文件中的AS号及其对应的列表
missing_asn_dict = {asn: line for asn, line in have_whois_dict.items() if asn not in have_whois_ipinfo_dict}

# 将结果写入新文件
output_file_path = '/mnt/data/missing_asn_list.txt'
with open(output_file_path, 'w') as file:
    for line in missing_asn_dict.values():
        file.write(line + '\n')

