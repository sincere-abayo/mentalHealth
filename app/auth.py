import base64
import requests
from requests.exceptions import RequestException
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Your credentials and key
api_user_id = '58a75be0-35cf-4140-bdce-fabce66976e6'
api_key = 'f0116eeaa3734d42b29a939d7e420643'
target_environment = "mtnrwanda"
key = "ad2c48fddd8f42ddbf5b917ae23ca431"
access_token = "no token found"

credentials = f"{api_user_id}:{api_key}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()
encoded_credentials = f'Basic {encoded_credentials}'

url = 'https://mtndeveloperapi.portal.mtn.co.rw/collection/token/'

headers = {
    'Authorization': encoded_credentials,
    'Ocp-Apim-Subscription-Key': key,
}

try:
    response = requests.post(url, headers=headers, verify=False)
    response.raise_for_status()

    # Get the response body
    response_body = response.json()
    
    # Extract and print only the access_token
    if 'access_token' in response_body:
        access_token = response_body['access_token']
        
        # print(access_token)
    else:
        access_token = "no token found"


except RequestException as ex:
    print(str(ex))
