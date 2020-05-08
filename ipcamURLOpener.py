import urllib.request

top_level_url = 'http://192.168.0.102:8080/'

password = "123"
username = "123"

urllib.request.HTTPPasswordMgrWithDefaultRealm()
password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
password_mgr.add_password(None, top_level_url, username, password)
handler = urllib.request.HTTPDigestAuthHandler(password_mgr)
opener = urllib.request.build_opener(handler)
urllib.request.install_opener(opener)

url = 'http://192.168.0.102:8080/shot.jpg'

