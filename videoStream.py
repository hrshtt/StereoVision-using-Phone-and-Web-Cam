import cv2 as cv
import urllib.request
import numpy as np
import ipcamURLOpener
from multiprocessing import Process

def phoneCamStream():
    url = ipcamURLOpener.url
    while(True):
        req = urllib.request.urlopen(url)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        img = cv.imdecode(arr, -1)
 
        cv.imshow('phoneStream', img)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

def webCameraStream():
    webcamCap = cv.VideoCapture(0)
    webcamCap.set(cv.CAP_PROP_FRAME_WIDTH,1280)
    webcamCap.set(cv.CAP_PROP_FRAME_HEIGHT,720)
    while(webcamCap.isOpened()):
        ret, frame = webcamCap.read()
        cv.imshow('webcamStreamun', frame)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    webcamCap.release()

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