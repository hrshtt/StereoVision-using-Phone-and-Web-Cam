import cv2 as cv
import urllib.request
import numpy as np
import ipcamURLOpener
from multiprocessing import Process

def phoneCamStream():
    url= 'http://192.168.0.102:8080/shot.jpg'
    while(True):
        req = urllib.request.urlopen(url)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        img = cv.imdecode(arr, -1)
 
        cv.imshow('phoneStream', img)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == "__main__": 
    top_level_url = 'http://192.168.0.102:8080/'

    password = "123"
    username = "123"

    urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, top_level_url, username, password)
    handler = urllib.request.HTTPDigestAuthHandler(password_mgr)
    opener = urllib.request.build_opener(handler)
    urllib.request.install_opener(opener)
    p1 = Process(target = phoneCamStream)
    
    p1.daemon = True

    p1.start()

    p1.join()

    cv.destroyAllWindows()