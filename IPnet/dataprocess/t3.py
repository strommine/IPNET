import csv
import json


# 读取IP地址列表
def read_ips_from_csv(filename):
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        ips = [row[0] for row in reader]
    return ips


# 读取每个IP地址的组织名称信息
def read_orgnames_from_txt(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = {}
        for line in f:
            item = json.loads(line.strip())
            for ip, info_list in item.items():
                for info in info_list:
                    for key in ["OrgName:", "org-name:", "Organization:"]:
                        if key in info:
                            data[ip] = info[key]
                            break
                if ip not in data:
                    data[ip] = ''
    return data


# 将组织名称写入CSV文件的第二列
def write_to_csv(input_filename, output_filename, orgnames):
    with open(input_filename, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    with open(output_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(rows[0] + ['org_name'])  # header
        for i, row in enumerate(rows[1:]):
            writer.writerow(row + [orgnames.get(row[0], '')])


# 主函数
def main():
    ips = read_ips_from_csv('D:/DoAc/whois/list.csv')
    orgnames = read_orgnames_from_txt('D:/DoAc/whois/outv4.txt')
    write_to_csv('D:/DoAc/whois/list.csv', 'D:/DoAc/whois/list_updated.csv', orgnames)


if __name__ == "__main__":
    main()
