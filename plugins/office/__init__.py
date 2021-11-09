import requests
from utils.utils import generate_ip, generate_id, generate_trace_id, get_office_headers


def validate(pluginargs, args):
    pluginargs = {'url' : "https://login.microsoft.com"}
    return True, None, pluginargs


def testconnect(pluginargs, args, api_dict, useragent):

    success = True
    headers = {
        'User-Agent': useragent,
        "X-My-X-Forwarded-For" : generate_ip(),
        "x-amzn-apigateway-api-id" : generate_id(),
        "X-My-X-Amzn-Trace-Id" : generate_trace_id(),
    }

    resp = requests.get(api_dict['proxy_url'], headers=headers)

    if resp.status_code == 504:
        output = "Testconnect: Connection failed, endpoint timed out, exiting"
        success = False
    else:
        output = "Testconnect: Connection success, continuting"
 
    if success:
        client_id, ctx, hpgid, hpgact, referrer, req_id = get_office_headers(useragent)
        if client_id and ctx and hpgid and hpgact and referrer and req_id:
            output = "Testconnect: Connection success, retrieve office headers success"
            pluginargs['client_id'] = client_id
            pluginargs['ctx'] = ctx
            pluginargs['hpgid'] = hpgid
            pluginargs['hpgact'] = hpgact
            pluginargs['referrer'] = referrer
            pluginargs['req_id'] = req_id
        else:
            output = "Testconnect: Connection success, but failed retrieving office headers"
            success = False

    return success, output, pluginargs
