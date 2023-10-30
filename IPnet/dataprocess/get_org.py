
# 获取网站证书中的组织名

import socket
import ssl
from urllib.parse import urlparse
from tqdm import tqdm


def get_certificate_organization(domain):
    context = ssl.create_default_context()
    conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=domain)
    conn.settimeout(3.0)  # Set a timeout for the connection
    conn.connect((domain, 443))
    cert = conn.getpeercert()
    conn.close()

    for field in cert['subject']:
        # Each field is a tuple, where the second element is a dictionary
        attribute_type, attribute_value = field[0]
        if attribute_type == 'organizationName':
            return attribute_value
    return None


def main():
    urls = []
    with open('D:\\DoAc\\roothtml\\urls.txt', 'r') as f:
        urls = f.readlines()

    with open('D:\\DoAc\\roothtml\\results.txt', 'w') as out_f, open('D:\\DoAc\\roothtml\\missing_orgs.txt', 'w') as missing_f:
        for url in tqdm(urls, desc="Processing URLs"):
            url = url.strip()
            domain = urlparse(url).netloc
            try:
                organization = get_certificate_organization(domain)
                if organization:
                    out_f.write(f'["{url}", "{organization}"]\n')
                else:
                    missing_f.write(f"{url}\n")
            except Exception as e:
                missing_f.write(f"{url} # Error: {e}\n")


if __name__ == "__main__":
    main()


