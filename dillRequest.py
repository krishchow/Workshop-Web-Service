import requests
import dill
import base64
import ast

url = 'http://127.0.0.1:5000/pythonObj'
headers = {'codeName':'fib5','key':'123456'}
r = requests.get(url, headers=headers)
data = r.json()['pythonCode']
data = ast.literal_eval(data)
data = base64.b64decode(data)

data = dill.loads(data)
print(data)