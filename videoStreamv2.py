import cv2 as cv
import urllib.request
import numpy as np
import ipcamURLOpener2,ipcamURLOpener
from multiprocessing import Process
import requests

def phoneCamStream():
    url= 'http://192.168.0.110:8080/shot.jpg'
    username = '123'
    password = '123'
    while(True):
        req = requests.get(url, auth=(username, password)).content
        decoded = cv.imdecode(np.frombuffer(req, np.uint8), -1)
        cv.imshow('phoneStream', decoded)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

def webCameraStream():
    url2= 'http://192.168.0.108:8080/shot.jpg'
    username = '123'
    password = '123'
    while(True):        
        req = requests.get(url2, auth=(username, password)).content
        decoded = cv.imdecode(np.frombuffer(req, np.uint8), -1)
        cv.imshow('phoneStream2', decoded)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == "__main__":

    p1 = Process(target = phoneCamStream)
    p2 = Process(target = webCameraStream)
    
    p1.daemon = True
    p2.daemon = True

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    cv.destroyAllWindows()