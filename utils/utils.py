import random, requests, re
from utils.ntlmdecode import ntlmdecode
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

def generate_ip():

    return ".".join(str(random.randint(0,255)) for _ in range(4))


def generate_id():

    return "".join(random.choice("0123456789abcdefghijklmnopqrstuvwxyz") for _ in range(10))


def generate_trace_id():
    str = "Root=1-"
    first = "".join(random.choice("0123456789abcdef") for _ in range(8))
    second = "".join(random.choice("0123456789abcdef") for _ in range(24))
    return str + first + "-" + second


def get_owa_domain(url, uri, useragent):
    # Stolen from https://github.com/byt3bl33d3r/SprayingToolkit who stole it from https://github.com/dafthack/MailSniper
    auth_header = {
        "Authorization": "NTLM TlRMTVNTUAABAAAAB4IIogAAAAAAAAAAAAAAAAAAAAAGAbEdAAAADw==",
        'User-Agent': useragent,
        "X-My-X-Forwarded-For" : generate_ip(),
        "x-amzn-apigateway-api-id" : generate_id(),
        "X-My-X-Amzn-Trace-Id" : generate_trace_id(),
    }

    r = requests.post("{url}{uri}".format(url=url,uri=uri), headers=auth_header, verify=False)
    if r.status_code == 401:
        ntlm_info = ntlmdecode(r.headers["x-amzn-Remapped-WWW-Authenticate"])
        return ntlm_info["NetBIOS_Domain_Name"]
    else:
        return "NOTFOUND"

def get_office_headers(useragent):
    auth_header = {
        'User-Agent': useragent
    }

    r = requests.get('https://www.office.com', headers=auth_header)
    client_id = re.findall(b'"appId":"([^"]*)"', r.content)

    data = {
        'es': 'Click',
        'ru': '/',
        'msafed': 0
    }
    r = requests.post('https://www.office.com/login', headers=auth_header, data=data, allow_redirects=True, verify=False)
    hpgid = re.findall(b'hpgid":([0-9]+),', r.content)
    hpgact = re.findall(b'hpgact":([0-9]+),', r.content)
    ctx = re.findall(b'"sCtx":"([^"]*)"', r.content)[0].decode('utf-8')
    referrer = r.url
    req_id = r.headers['x-ms-request-id']

    if client_id and hpgid and hpgact and ctx and req_id:
        return str(client_id[0].decode()), str(ctx), str(hpgid[0].decode()), str(hpgact[0].decode()), str(referrer), str(req_id)
    else:
        print('An error occured when generating headers')
        return None, None, None, None, None, None
