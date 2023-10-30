import ipaddress
import json
import dns.resolver
import dns.reversename
import concurrent.futures
from tqdm import tqdm

dns_server = '8.8.8.8'
htimes = 100
hnumber = 100000
start_ipv6 = '2803:9200:1::6'


def is_valid_ipv6(address):
    try:
        ipaddress.IPv6Address(address)
        return True
    except ipaddress.AddressValueError:
        return False


def get_ptr(ip):
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [dns_server]
        rev_name = dns.reversename.from_address(ip)
        ptr_name = str(resolver.resolve(rev_name, "PTR")[0])
        return ptr_name
    except (dns.resolver.NXDOMAIN, dns.resolver.Timeout, dns.exception.SyntaxError):
        return None


def ipv6_generator(file_path):
    start = False
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line == start_ipv6:
                start = True
            if start and is_valid_ipv6(line):
                yield line


def ipv6_to_ptr(file_path, result_path, handle_times):
    results = {}
    valid_count = 0
    total = htimes * hnumber

    ipv6_gen = ipv6_generator(file_path)
    with tqdm(total=total) as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            for _ in range(handle_times):
                future_to_ip = {executor.submit(get_ptr, ip): ip for _, ip in zip(range(hnumber), ipv6_gen)}
                for future in concurrent.futures.as_completed(future_to_ip):
                    ip = future_to_ip[future]
                    try:
                        results[ip] = future.result()
                    except Exception as exc:
                        continue
                    pbar.update()

                    # 判断是否需要写入到磁盘
                    if len(results) >= hnumber:
                        with open(result_path, 'a') as f:
                            for key, value in results.items():
                                f.write(json.dumps({key: value}))
                                f.write('\n')
                        results = {}  # 清空 results

    if results:  # 将剩余的结果写入到磁盘
        with open(result_path, 'a') as f:
            for key, value in results.items():
                f.write(json.dumps({key: value}))
                f.write('\n')

    valid_count = list(results.values()).count(None)
    print(f'获取到PTR记录的IPv6地址的比例: {(total - valid_count) / total * 100:.2f}%')


ipv6_to_ptr('D:/DoAc/responsive-addresses.txt', 'D:/DoAc/allptr.txt', htimes)
