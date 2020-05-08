import urllib.request

top_level_url_2 = 'http://192.168.0.108:8080/'

password = "123"
username = "123"

password_mgr_2 = urllib.request.HTTPPasswordMgrWithDefaultRealm()
password_mgr_2.add_password(None, top_level_url_2, username, password)
handler_2 = urllib.request.HTTPDigestAuthHandler(password_mgr_2)
opener_2 = urllib.request.build_opener(handler_2)
urllib.request.install_opener(opener_2)

url_2 = 'http://192.168.0.108:8080/shot.jpg'