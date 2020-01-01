import requests, json, base64
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

verifySSL = True
headers = {}

def login(user, passwd):
    global session_id, headers
    res = requests.post(base_url + 'WebServices/auth/Cyberark/CyberArkAuthenticationService.svc/Logon', json = { "username": user, "password": passwd }, verify = verifySSL)
    if (res.status_code == 200):
        session_id = (res.json())['CyberArkLogonResult']
        headers = {'Authorization': session_id}
        return True
    else:
        return False
        
def logout():
    res = requests.post(base_url + 'WebServices/auth/Cyberark/CyberArkAuthenticationService.svc/Logoff', headers = headers, verify = verifySSL)
    if (res.status_code == 200):
        return True
    else:
        return False
        
def list_safes():
    res = requests.get(base_url + 'WebServices/API.svc/Safes', headers = headers, verify = verifySSL)
    return res.json()
    
def list_objects(safe_name):
    res = requests.get(base_url + 'WebServices/API.svc/Safes/' + safe_name + '/Content', headers = headers, verify = verifySSL)
    return res.json()
    
def download_file(file_name, share_url):
    global download_directory
    with requests.get(base_url + '/' + share_url, headers = headers, stream = True, verify = verifySSL) as r:
        r.raise_for_status()
        with open(download_directory + '/' + file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                if chunk:
                    f.write(chunk)
                    f.flush()
    return file_name

session_id = ''
host = '{cyberark-sfe-address}'
base_url = 'https://' + host + '/SFE/'
download_directory = '/tmp/files/'
safe_name = '{safe-name}'

if login('{username}', '{password}'):
    print('logged-in successfully.')
    for file in list_objects(safe_name):
        if 'ContentType' not in file:
            errors.append(safe_name)
        else:
            if file['ContentType'] == 2:
                print ('downloading \'' + file['ContentName'] + '\'...')
                download_file(file['ContentName'], file['ShareURL'])
    
    if logout():
        print('logged-out successfully.')
    else:
        print('logout failed')
    
else:
    print('login failed')

print('\nthank you, come again :)')
