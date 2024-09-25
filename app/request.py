import uuid
import requests
from requests.exceptions import RequestException
from flask import Flask, session

# Assuming you have the access_token from auth.py
from auth import access_token, key, target_environment
app = Flask(__name__)
app.secret_key = 'abcdfrtyujjjghggggffgdddsfdf'  # Set a secret key for session management


number = "0784424423"
# number = "0784424423"
amount = 300
amount = int(amount)


# Generate a version 4 (random) UUID
reference_id = str(uuid.uuid4())

authorization = f'Bearer {access_token}'

# Store authorization and reference_id in session
session['authorization'] = authorization
session['reference_id'] = reference_id

unique_id = str(uuid.uuid4().int)[:5]  # Generate a 5-digit unique ID



request_body = {
    "amount": amount,
    "currency": "RWF",
    "externalId": unique_id,
    "payer": {
        "partyIdType": "MSISDN",
        "partyId": number,
    },
    "payerMessage": "Payment for ticket",
    "payeeNote": f"Invoice {unique_id}",
}

headers = {
    'Authorization': authorization,
    # 'X-Callback-Url': 'http://localhost/clemant/update.php',
    'X-Reference-Id': reference_id,
    'X-Target-Environment': target_environment,
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': key,
    }

url = 'https://mtndeveloperapi.portal.mtn.co.rw/collection/v1_0/requesttopay'

try:
    response = requests.post(url, headers=headers, json=request_body, verify=False)
    response.raise_for_status()

    # Get the response body
    response_body = response.text
    if response:
        print(response.status_code)
    else:
        print("The response is empty.")

except RequestException as ex:
    print(str(ex))
