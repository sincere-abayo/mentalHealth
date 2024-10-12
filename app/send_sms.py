import requests

data = {
           'recipients': '0732286284',
           'message': 'Hello World',
           'sender': 'MHPCM System  '
        }
username = "josianedev"
password ="Josiane@21"
r = requests.post(
           'https://www.intouchsms.co.rw/api/sendsms/.json',
           data,
           auth=(username, password)
)

print(r.json(), r.status_code)