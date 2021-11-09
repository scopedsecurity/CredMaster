import datetime, requests, random, string
from utils.utils import generate_ip, generate_id, generate_trace_id


def office_authenticate(url, username, password, useragent, pluginargs):
    
    ts = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    data_response = {
        'timestamp': ts,
        'username': username,
        'password': password,
        'success': False,
        'change': False,
        '2fa_enabled': False,
        'type': None,
        'code': None,
        'name': None,
        'action': None,
        'headers': [],
        'cookies': [],
        'sourceip': None,
        'throttled': False,
        'error': False,
        'output': ""
    }

    body = {
        'isOtherIdpSupported': True,
        'checkPhones': False,
        'isRemoteNGCSupported': True,
        'isCookieBannerShown': False,
        'isFidoSupported': False,
        'originalRequest': pluginargs['ctx'],
        'forceotclogin': False,
        'isExternalFederationDisallowed': False,
        'isRemoteConnectSupported': False,
        'federationFlags': 0,
        'isSignup': False,
        'isAccessPassSupported': True,
        'mkt': 'en-US',
        'username': username
    }
    
    spoofed_ip = generate_ip()
    amazon_id = generate_id()
    trace_id = generate_trace_id()

    headers = {
        'X-My-X-Forwarded-For' : spoofed_ip,
        'x-amzn-apigateway-api-id' : amazon_id,
        'X-My-X-Amzn-Trace-Id' : trace_id,
        'User-Agent': useragent,
        'Referer': pluginargs['referrer'],
        'client-request-id': pluginargs['client_id'],
        'hpgid': pluginargs['hpgid'],
        'hpgact': pluginargs['hpgact'],
        'hpgrequestid': pluginargs['req_id'],
        'canary': ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits + "-_") for i in range(248)),
        'Accept': 'application/json',
        'Origin': 'https://login.microsoftonline.com'
    }
    
    try:
        resp = requests.post('{}/common/GetCredentialType'.format(url), headers=headers, json=body)
        data_response['code'] = resp.status_code
        
        if resp.status_code == 200:
            result_json = resp.json()
            res_exists = result_json.get('IfExistsResult')
            if res_exists is not None:
                if int(res_exists) in (0, 5, 6):
                    data_response['success'] = True
                    data_response['output'] = f'SUCCESS! Username: {username} exists.' 
                elif int(res_exists) == 1:
                    data_response['success'] = False
                    data_response['output'] = f'FAILED. Username: {username} does not exist.' 
                else:
                    data_response['success'] = False
                    data_response['output'] = f'FAILED. Username: {username} unknown response.' 
            else:
                data_response['success'] = False
                data_response['output'] = f'FAILED. Username: {username} unknown response.' 
        else:
            data_response['success'] = False
            data_response['output'] = f'FAILED. Username: {username} unknown response.' 
    
    except Exception as ex:
        data_response['error'] = True
        data_response['output'] = ex
        pass

    return data_response
