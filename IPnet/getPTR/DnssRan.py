import ipaddress
import json
import dns.resolver
import dns.reversename
import concurrent.futures
from tqdm import tqdm
import random

dns_server = '8.8.8.8'
htimes = 10
hnumber = 10000


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


def ipv6_sample(file_path):
    sample = []
    batch_size = 100  # 每100行
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for i in range(0, len(lines), batch_size):
            batch = lines[i:i + batch_size]
            valid_ipv6 = [line.strip() for line in batch if is_valid_ipv6(line.strip())]
            if valid_ipv6:
                sample.append(random.choice(valid_ipv6))
    return sample


def ipv6_to_ptr(file_path, result_path, error_path):
    results = {}
    errors = []
    valid_count = 0
    total = htimes * hnumber

    # 随机采样
    ipv6_gen = ipv6_sample(file_path)

    with tqdm(total=total) as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            for i in range(htimes):
                future_to_ip = {executor.submit(get_ptr, ip): ip for ip in ipv6_gen[i * hnumber:(i + 1) * hnumber]}
                for future in concurrent.futures.as_completed(future_to_ip):
                    ip = future_to_ip[future]
                    try:
                        results[ip] = future.result()
                    except Exception as exc:
                        # 发生异常
                        errors.append(ip)
                    pbar.update()

                if len(results) >= hnumber:
                    with open(result_path, 'a') as f:
                        for key, value in results.items():
                            f.write(json.dumps({key: value}))
                            f.write('\n')
                    valid_count += list(results.values()).count(None)
                    results = {}  # 清空 results

    if results:  # 将剩余的结果写入到磁盘
        with open(result_path, 'a') as f:
            for key, value in results.items():
                f.write(json.dumps({key: value}))
                f.write('\n')
        valid_count += list(results.values()).count(None)

    # 异常的IPv6地址写入
    with open(error_path, 'w') as f:
        for error in errors:
            f.write(error + '\n')

    error_count = len(errors)
    print(f'获取到PTR记录的IPv6地址的比例: {(total - valid_count) / total * 100:.2f}%')
    print(f'异常的IPv6地址的比例: {error_count / total * 100:.2f}%')


ipv6_to_ptr('D:/DoAc/responsive-addresses.txt', 'D:/DoAc/div-ptr.txt', 'D:/DoAc/div-errptr.txt')
