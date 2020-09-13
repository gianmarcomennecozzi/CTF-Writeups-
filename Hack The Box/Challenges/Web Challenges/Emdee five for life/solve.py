#!/usr/bin/env python3

import requests
import re
import hashlib 


URL = "http://docker.hackthebox.eu:32464/"
req = requests.session()
resp = req.get(URL)

content = re.search(r"<h3 align='center'>(.+?)</h3>", resp.text).group(1)
result = hashlib.md5(content.encode()) 

data = {'hash': result.hexdigest()}

new_resp = req.post(URL, data)
print(new_resp.text)
