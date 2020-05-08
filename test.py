import requests
url = 'http://192.168.0.108:8080/shot.jpg'
username = '123'
password = '123'


print(type(requests.get(url, auth=(username, password)).content))