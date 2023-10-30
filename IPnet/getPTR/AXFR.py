import dns.query
import dns.zone
import dns.resolver
import dns.reversename


def get_ns_and_axfr(ipv6):
    try:
        rev_name = dns.reversename.from_address(ipv6)
        ptr_name = str(dns.resolver.resolve(rev_name, "PTR")[0])
        domain = ptr_name.split('.', 1)[1]
        ns_set = dns.resolver.resolve(domain, 'NS')

        for ns in ns_set:
            ns_name = ns.to_text()[:-1]

            try:
                # 获取域的 AXFR 记录
                zone = dns.zone.from_xfr(dns.query.xfr(ns_name, domain))
                print(f"AXFR succeeded on server {ns_name}")

                for name, node in zone.nodes.items():
                    rdatasets = node.rdatasets
                    for rdataset in rdatasets:
                        print(f"{name} {rdataset}")

            except Exception as e:
                print(f"AXFR failed on server {ns_name} due to: {str(e)}")

    except Exception as e:
        print(f"Failed to fetch PTR record for {ipv6} due to: {str(e)}")


get_ns_and_axfr('2001:1218:1000:500::133')
