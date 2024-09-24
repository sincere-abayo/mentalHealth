import urllib.request, json

try:
    url = "https://sandbox.momodeveloper.mtn.co.rw/collection/v1_0/requesttopay"

    hdr ={
    # Request headers
    'Authorization': 'Basic NThhNzViZTAtMzVjZi00MTQwLWJkY2UtZmFiY2U2Njk3NmU2OmYwMTE2ZWVhYTM3MzRkNDJiMjlhOTM5ZDdlNDIwNjQz',
    'Ocp-Apim-Subscription-Key': '3b7f23556ab24875bb12089f6db56926',
    }

    req = urllib.request.Request(url, headers=hdr)

    req.get_method = lambda: 'POST'
    response = urllib.request.urlopen(req)
    print(response.getcode())
    print(response.read())
except Exception as e:
    print(e)