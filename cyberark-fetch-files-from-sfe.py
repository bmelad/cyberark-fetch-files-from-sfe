import requests, json, base64
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

verifySSL = False
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
    
def download_file(safe_name, file_name, file_id):
    global download_directory
    with requests.get(base_url + 'WebServices/API.svc/Safes/' + safe_name + '/Files/' + str(file_id) + '/Stream', headers = headers, stream = True, verify = verifySSL) as res:
        res.raise_for_status()
        with open(download_directory + '\\' + file_name, 'wb') as f:
            for chunk in res.iter_content(chunk_size=8192): 
                if chunk:
                    f.write(chunk)
                    f.flush()
    return (res.status_code == 200)

def delete_file(safe_name, file_id):
    res = requests.delete(base_url + 'WebServices/API.svc/Safes/' + safe_name + '/Files/' + str(file_id), headers = headers, verify = verifySSL)
    return (res.status_code == 200)

session_id = ''
username = '{username}'
password = '{password}'
host = '{cyberark-sfe-address}'
base_url = 'https://' + host + '/SFE/'
download_directory = '/tmp/files/'
safe_name = '{safe-name}'
delete_after_download = False

if login(username, password):
    print('logged-in successfully.')
    for file in list_objects(safe_name):
        if 'ContentType' not in file:
            errors.append(safe_name)
        else:
            if file['ContentType'] == 2:
                print ('downloading \'' + file['ContentName'] + '\'...', end='')
                if not download_file(safe_name, file['ContentName'], file['ContentID']):
                    print(' failed.')
                else:
                    print(' done.')
                    if delete_after_download:
                        print('   deleting \'' + file['ContentName'] + '\' from safe...', end='')
                        if not delete_file(safe_name, file['ContentID']):
                            print(' failed.')
                        else:
                            print(' done.')
    if logout():
        print('logged-out successfully.')
    else:
        print('logout failed')
    
else:
    print('login failed')

print('\nthank you, come again :)')
