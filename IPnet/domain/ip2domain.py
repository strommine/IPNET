import ssl
import json
import OpenSSL

records = []
with open("../data/result.json", "r") as f:
        results = json.load(f)
with open("../data/query_url.txt", "r") as f:
    str_ = f.readline()
    while str_:
        records.append(json.loads(str_))
        str_ = f.readline()
# 主机和端口
# host = 'www.baidu.com'
port = 443
# cnt = 0
# o_cnt = 0
x509_cnt = 0
x509_o_cnt = 0

with open("../data/err_log.txt", "a+") as err_log:
    for record in records:
        if record["ipv6"] in results:
            continue
        if len(record["urls"]) == 0:
            print("get urls: None" + " " + record["ipv6"], file=err_log)
            continue
        host = record["urls"][0].replace("https://", "").replace("http://", "")
        try:
            cert = ssl.get_server_certificate((host, port), ca_certs=None, timeout=20)
            if not cert:
                print("get Certificate: None" + " " + host, file=err_log)
                continue
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
            x509_cnt += 1

            # get org info
            flag = False
            on = ""
            cn = ""
            san = ""
            # ON: organizationName
            if x509.get_subject().organizationName:
                flag = True
                on = x509.get_subject().organizationName
            # CN: commonName
            if x509.get_subject().commonName:
                flag = True
                cn = x509.get_subject().commonName
            # SAN: subjectAltName
            ext_cnt = x509.get_extension_count()
            for i in range(ext_cnt):
                ext = x509.get_extension(i)
                if ext.get_short_name() == b"subjectAltName":
                    san = str(ext)
                    flag = True
                    break
            if not flag:
                print("get subjectInfo: None" + " " + host, file=err_log)
            else:
                x509_o_cnt += 1
                if record["ipv6"] not in results:
                    results[record["ipv6"]] = {}
                results[record["ipv6"]]["on"] = on
                results[record["ipv6"]]["cn"] = cn
                results[record["ipv6"]]["san"] = san
                results[record["ipv6"]]["url"] = record["urls"][0]
                print("{} / {}".format(x509_o_cnt, x509_cnt))
        except Exception as e:
            print(str(e) + " " + host, file=err_log)
            print(str(e) + " " + host)

with open("result.json", "w") as f:
    json.dump(results, f, indent=4)


print("{} / {}".format(x509_o_cnt, x509_cnt))
