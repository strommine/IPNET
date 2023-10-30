import ipaddress
import json
import dns.resolver
import dns.reversename
import concurrent.futures
from tqdm import tqdm


def is_valid_ipv6(address):
    try:
        ipaddress.IPv6Address(address)
        return True
    except ipaddress.AddressValueError:
        return False


def get_ptr(ip):
    try:
        rev_name = dns.reversename.from_address(ip)
        ptr_name = str(dns.resolver.resolve(rev_name, "PTR")[0])
        return ptr_name
    except (dns.resolver.NXDOMAIN, dns.resolver.Timeout, dns.exception.SyntaxError):
        return None


def ipv6_to_ptr(file_path, result_path):
    results = {}
    total = 0
    valid_count = 0

    with open(file_path, 'r') as f:
        lines = f.read().splitlines()
        total = len(lines)
        with tqdm(total=total) as pbar:
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                future_to_ip = {executor.submit(get_ptr, ip): ip for ip in lines if is_valid_ipv6(ip)}
                for future in concurrent.futures.as_completed(future_to_ip):
                    ip = future_to_ip[future]
                    try:
                        results[ip] = future.result()
                    except Exception as exc:
                        print(f'Error occurred while fetching PTR record for {ip}: {exc}')
                    pbar.update()

    with open(result_path, 'w') as f:
        f.write(json.dumps(results, indent=4))

    valid_count = list(results.values()).count(None)
    print(f'获取到PTR记录的IPv6地址的比例: {(total - valid_count) / total * 100:.2f}%')


ipv6_to_ptr('D:/DoAc/ipv6.txt', 'D:/DoAc/result2.txt')
