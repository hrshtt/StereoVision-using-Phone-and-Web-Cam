import cv2 as cv
import urllib.request
import numpy as np
import ipcamURLOpener
from time import sleep
import pickle

IMAGE_SIZE = (1280, 720)
ANS = {"y": True,
    "Y": True,
    "N": False,
    "n": False}
ALPHA = 0

def getCameraCalibration():
    recalc = str(input("Calculate New Camera Calibration Points? Y/N: "))
    if ANS[recalc]:
        objpoints, phonecamImgPoints, webcamImgPoints =  getChessPatternPoints("camCalibPoints")

        phonecamPara = cv.calibrateCamera(objpoints, phonecamImgPoints, IMAGE_SIZE, None, None)
        webcamPara = cv.calibrateCamera(objpoints, webcamImgPoints, IMAGE_SIZE, None, None)

        saveCamPara = input("Save camera Parameters? Y/N: ")
        
        if ANS[saveCamPara]:
            with open("./camera_params/phonecamParams", "wb") as file:
                pickle.dump(phonecamPara, file)
            file.close()
            with open("./camera_params/webcamParams", "wb") as file:
                pickle.dump(webcamPara, file)
            file.close()
        return(phonecamPara, webcamPara)

    else:
        with open("./camera_params/phonecamParams", "rb") as file:
            phonecamPara = pickle.load(file)
        file.close()
        with open("./camera_params/webcamParams", "rb") as file:
            webcamPara = pickle.load(file)
        file.close()
        return(phonecamPara, webcamPara)

def getStereoCalibration(phonecamPara, webcamPara):

    phonecam = {}
    webcam = {}
    ret , phonecam['camMtx'], phonecam['distMtx'], phonecam['rotMtx'], phonecam['trnsMrx'] = phonecamPara
    ret , webcam['camMtx'], webcam['distMtx'], webcam['rotMtx'], webcam['trnsMrx'] = webcamPara

    phonecam['optCamMtx'], phonecam['roi'] = cv.getOptimalNewCameraMatrix(
        phonecam['camMtx'], 
        phonecam['distMtx'], 
        IMAGE_SIZE, 
        alpha = ALPHA)

    webcam['optCamMtx'], webcam['roi'] = cv.getOptimalNewCameraMatrix(
        webcam['camMtx'], 
        webcam['distMtx'], 
        IMAGE_SIZE, 
        alpha = ALPHA)

    recalc = str(input("Calculate New Stereo Calibration Points? Y/N: "))

    if ANS[recalc]:
        objpoints, phonecamImgPoints, webcamImgPoints =  getChessPatternPoints("stereoCamCalibPoints")

        ret, _ , _ , _ , _ , rotMtx, trnsMtx, _ , _ = cv.stereoCalibrate(
            objpoints,
            webcamImgPoints, 
            phonecamImgPoints, 
            webcam['optCamMtx'], 
            webcam['distMtx'], 
            phonecam['optCamMtx'], 
            phonecam['distMtx'], 
            IMAGE_SIZE ,
            flags=cv.CALIB_FIX_INTRINSIC + cv.CALIB_FIX_FOCAL_LENGTH + cv.CALIB_FIX_ASPECT_RATIO)

        webcam['stereoRectRotMtx'], phonecam['stereoRectRotMtx'], webcam['projMtx'], phonecam['projMtx'], Q , webcam['stereoROI'] , _ = cv.stereoRectify(
            webcam['camMtx'],
            webcam['distMtx'],
            phonecam['camMtx'],
            phonecam['distMtx'],
            IMAGE_SIZE, 
            rotMtx, 
            trnsMtx,
            # flags= cv.CALIB_ZERO_DISPARITY, 
            alpha = ALPHA)

        phoneCamStereoMap = cv.initUndistortRectifyMap(
            phonecam['camMtx'], 
            phonecam['distMtx'], 
            phonecam['stereoRectRotMtx'], 
            phonecam['projMtx'], 
            IMAGE_SIZE, 
            cv.CV_16SC2)

        webCamStereoMap = cv.initUndistortRectifyMap(
            webcam['camMtx'],
            webcam['distMtx'], 
            webcam['stereoRectRotMtx'], 
            webcam['projMtx'], 
            IMAGE_SIZE, 
            cv.CV_16SC2)

        saveCamPara = input("Save Stereo Camera Parameters? Y/N: ")
        
        if ANS[saveCamPara]:
            with open("./camera_params/phoneCamStereoMap", "wb") as file:
                pickle.dump(phoneCamStereoMap, file)
            file.close()
            with open("./camera_params/webCamStereoMap", "wb") as file:
                pickle.dump(webCamStereoMap, file)
            file.close()
        return(phoneCamStereoMap, webCamStereoMap)

    else:
        with open("./camera_params/phoneCamStereoMap", "rb") as file:
            phoneCamStereoMap = pickle.load(file)
        file.close()
        with open("./camera_params/webCamStereoMap", "rb") as file:
            webCamStereoMap = pickle.load(file)
        file.close()
        return(phoneCamStereoMap, webCamStereoMap)

def getChessPatternPoints(location):

    url = ipcamURLOpener.url 
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    webcamImgPoints = [] # 2d points in image plane.
    phonecamImgPoints = [] # 2d points in image plane.
    objpoints = [] # 3d point in real world space
    
    objp = np.zeros((6*9,3), np.float32)
    objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)

    webcamCap = cv.VideoCapture(0)
    webcamCap.set(cv.CAP_PROP_FRAME_WIDTH,1280)
    webcamCap.set(cv.CAP_PROP_FRAME_HEIGHT,720)
    i = 0
    saveImages = input("Save the Images? Y/N: ")

    while(True):
        req = urllib.request.urlopen(url)
        ret = webcamCap.grab()
        
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        phonecamFrame = cv.imdecode(arr, -1)
        ret, webcamFrame = webcamCap.retrieve()
 
        phonecamGray = cv.cvtColor(phonecamFrame, cv.COLOR_BGR2GRAY)
        webcamGray = cv.cvtColor(webcamFrame, cv.COLOR_BGR2GRAY)

        ret1, phonecamCorners = cv.findChessboardCorners(phonecamGray, (9,6), None)
        ret2, webcamCorners = cv.findChessboardCorners(webcamGray, (9,6), None)

        if ret1 and ret2:
            

            new_corners1 = cv.cornerSubPix(phonecamGray,phonecamCorners, (11,11), (-1,-1), criteria)
            new_corners2 = cv.cornerSubPix(webcamGray,webcamCorners, (11,11), (-1,-1), criteria)

            # if cv.waitKey(1) & 0xFF == ord('s'):
            i = i + 1
            objpoints.append(objp)
            phonecamImgPoints.append(new_corners1) 
            webcamImgPoints.append(new_corners2) 
            if ANS[saveImages]:
                cv.imwrite("./images/"+ location + "/image-left-" + str(i) + ".jpeg", webcamFrame)
                cv.imwrite("./images/"+ location + "/image-right-" + str(i)+ ".jpeg", phonecamFrame)
            print(i)
            # sleep(3)

            cv.drawChessboardCorners(phonecamFrame, (9,6), new_corners1, ret)
            cv.drawChessboardCorners(webcamFrame, (9,6), new_corners2, ret)

        cv.imshow('phoneStream', phonecamFrame)
        cv.imshow('webcamStream', webcamFrame)

        if cv.waitKey(1) & 0xFF == ord('q'):
            cv.destroyAllWindows()
            webcamCap.release()
            break
    return(objpoints, phonecamImgPoints, webcamImgPoints)

def saveSnapshot():
    url = ipcamURLOpener.url 

    webcamCap = cv.VideoCapture(0)
    webcamCap.set(cv.CAP_PROP_FRAME_WIDTH,1280)
    webcamCap.set(cv.CAP_PROP_FRAME_HEIGHT,720)

    req = urllib.request.urlopen(url)
    ret = webcamCap.grab()

    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    img = cv.imdecode(arr, -1)

    x, frame  = webcamCap.retrieve()
    webcamCap.release()
    cv.imwrite("image1.jpeg",img)
    cv.imwrite("image2.jpeg",frame)

    while(True):
        cv.imshow("webcamShot", frame)
        cv.imshow("phonecamShot", img)
        if cv.waitKey(1) & 0xFF == ord('q'):
            cv.destroyAllWindows()
            break

if __name__ == "__main__": 
    
    phonecam = {}
    webcam = {}

    phonecamPara, webcamPara = getCameraCalibration()

    [phonecam['map1'], phonecam['map2']], [webcam['map1'], webcam['map2']] = getStereoCalibration( phonecamPara, webcamPara)

    takeSnap = input("Take new Snapshots? Y/N: ")
    if ANS[takeSnap]:
        sleep(2)
        saveSnapshot()
        
    testImg1 = cv.imread("image1.jpeg")
    testImg2 = cv.imread("image2.jpeg")
    
    rectifiedImage1 = cv.remap(testImg1, phonecam['map1'], phonecam['map2'], cv.INTER_NEAREST)
    rectifiedImage2 = cv.remap(testImg2, webcam['map1'], webcam['map2'], cv.INTER_NEAREST)
   
    vis = np.concatenate((rectifiedImage1, rectifiedImage2), axis= 1)
    
    # cv.imwrite("tempImg.jpeg", vis)

    while(True):
        cv.imshow("stereo", vis)
        if cv.waitKey(1) & 0xFF == ord('q'):
            cv.destroyAllWindows()
            break
