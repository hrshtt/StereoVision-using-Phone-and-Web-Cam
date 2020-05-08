import cv2 as cv
import numpy as np
from time import sleep
import pickle
import requests

IMAGE_SIZE = (1280, 720)

URL = {
    'phoneOne': 'http://192.168.0.110:8080/shot.jpg'
    'phoneTwo': 'http://192.168.0.108:8080/shot.jpg'
}

ANS = {"y": True,
    "Y": True,
    "N": False,
    "n": False}
    
ALPHA = 0

def getCameraCalibration():
    recalc = str(input("Calculate New Camera Calibration Points? Y/N: "))
    if ANS[recalc]:
        objpoints, phoneOneImgPoints, phoneTwoImgPoints =  getChessPatternPoints("camCalibPoints")

        phoneOnePara = cv.calibrateCamera(objpoints, phoneOneImgPoints, IMAGE_SIZE, None, None)
        phoneTwoPara = cv.calibrateCamera(objpoints, phoneTwoImgPoints, IMAGE_SIZE, None, None)

        saveCamPara = input("Save camera Parameters? Y/N: ")
        
        if ANS[saveCamPara]:
            with open("./camera_params/phoneOneParams", "wb") as file:
                pickle.dump(phoneOnePara, file)
            file.close()
            with open("./camera_params/phoneTwoParams", "wb") as file:
                pickle.dump(phoneTwoPara, file)
            file.close()
        return(phoneOnePara, phoneTwoPara)

    else:
        with open("./camera_params/phoneOneParams", "rb") as file:
            phoneOnePara = pickle.load(file)
        file.close()
        with open("./camera_params/phoneTwoParams", "rb") as file:
            phoneTwoPara = pickle.load(file)
        file.close()
        return(phoneOnePara, phoneTwoPara)

def getStereoCalibration(phoneOnePara, phoneTwoPara):

    phoneOne = {}
    phoneTwo = {}
    ret, phoneOne['camMtx'], phoneOne['distMtx'], _, _ = phoneOnePara
    ret, phoneTwo['camMtx'], phoneTwo['distMtx'], _, _ = phoneTwoPara

    phoneOne['optCamMtx'], _ = cv.getOptimalNewCameraMatrix(
        phoneOne['camMtx'], 
        phoneOne['distMtx'], 
        IMAGE_SIZE, 
        alpha = ALPHA)

    phoneTwo['optCamMtx'], _ = cv.getOptimalNewCameraMatrix(
        phoneTwo['camMtx'], 
        phoneTwo['distMtx'], 
        IMAGE_SIZE, 
        alpha = ALPHA)

    recalc = str(input("Calculate New Stereo Calibration Points? Y/N: "))

    if ANS[recalc]:
        objpoints, phoneOneImgPoints, phoneTwoImgPoints =  getChessPatternPoints("stereoCamCalibPoints")

        ret, _ , _ , _ , _ , rotMtx, trnsMtx, _ , _ = cv.stereoCalibrate(
            objpoints,
            phoneOneImgPoints, 
            phoneTwoImgPoints, 
            phoneOne['optCamMtx'], 
            phoneOne['distMtx'], 
            phoneTwo['optCamMtx'], 
            phoneTwo['distMtx'], 
            IMAGE_SIZE,
            flags = cv.CALIB_FIX_INTRINSIC + cv.CALIB_FIX_FOCAL_LENGTH + cv.CALIB_FIX_ASPECT_RATIO)

        phoneOne['stereoRectRotMtx'], phoneTwo['stereoRectRotMtx'], phoneOne['projMtx'], phoneTwo['projMtx'], Q , phoneTwo['stereoROI'] , _ = cv.stereoRectify(
            phoneOne['camMtx'],
            phoneOne['distMtx'],
            phoneTwo['camMtx'],
            phoneTwo['distMtx'],
            IMAGE_SIZE, 
            rotMtx, 
            trnsMtx,
            flags= cv.CALIB_ZERO_DISPARITY, 
            alpha = ALPHA)

        phoneOneStereoMap = cv.initUndistortRectifyMap(
            phoneOne['camMtx'], 
            phoneOne['distMtx'], 
            phoneOne['stereoRectRotMtx'], 
            phoneOne['projMtx'], 
            IMAGE_SIZE, 
            cv.CV_16SC2)

        phoneTwoStereoMap = cv.initUndistortRectifyMap(
            phoneTwo['camMtx'],
            phoneTwo['distMtx'], 
            phoneTwo['stereoRectRotMtx'], 
            phoneTwo['projMtx'], 
            IMAGE_SIZE, 
            cv.CV_16SC2)

        saveCamPara = input("Save Stereo Camera Parameters? Y/N: ")
        
        if ANS[saveCamPara]:
            with open("./camera_params/phoneOneStereoMap", "wb") as file:
                pickle.dump(phoneOneStereoMap, file)
            file.close()
            with open("./camera_params/phoneTwoStereoMap", "wb") as file:
                pickle.dump(phoneTwoStereoMap, file)
            file.close()
        return(phoneOneStereoMap, phoneTwoStereoMap)

    else:
        with open("./camera_params/phoneOneStereoMap", "rb") as file:
            phoneOneStereoMap = pickle.load(file)
        file.close()
        with open("./camera_params/phoneTwoStereoMap", "rb") as file:
            phoneTwoStereoMap = pickle.load(file)
        file.close()
        return(phoneOneStereoMap, phoneTwoStereoMap)

def getChessPatternPoints(location):

    phoneOne = {}
    phoneTwo = {}

    phoneOne['url']= URL['phoneOne']
    phoneTwo['url']= URL['phoneTwo']

    username = '123'
    password = '123'

    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    phoneOne['imgPoints'] = [] # 2d points in image plane.
    phoneTwo['imgPoints'] = [] # 2d points in image plane.
    objpoints = [] # 3d point in real world space
    
    objp = np.zeros((6*9,3), np.float32)
    objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)

    i = 0
    saveImages = input("Save the Images? Y/N: ")

    while(True):
        
        req1 = requests.get(phoneOne['url'], auth=(username, password)).content
        phoneOne['img'] = cv.imdecode(np.frombuffer(req1, np.uint8), -1)

        req2 = requests.get(phoneTwo['url'], auth=(username, password)).content
        phoneTwo['img'] = cv.imdecode(np.frombuffer(req2, np.uint8), -1)
 
        phoneOneGray = cv.cvtColor(phoneOne['img'], cv.COLOR_BGR2GRAY)
        phoneTwoGray = cv.cvtColor(phoneTwo['img'], cv.COLOR_BGR2GRAY)

        ret1, phoneOneCorners = cv.findChessboardCorners(phoneOneGray, (9,6), None)
        ret2, phoneTwoCorners = cv.findChessboardCorners(phoneTwoGray, (9,6), None)

        if ret1 and ret2:
            

            new_corners1 = cv.cornerSubPix(phoneOneGray,phoneOneCorners, (11,11), (-1,-1), criteria)
            new_corners2 = cv.cornerSubPix(phoneTwoGray,phoneTwoCorners, (11,11), (-1,-1), criteria)

            if cv.waitKey(1) & 0xFF == ord('s'):
                i = i + 1
                objpoints.append(objp)
                phoneOne['imgPoints'].append(new_corners1) 
                phoneTwo['imgPoints'].append(new_corners2)
                if ANS[saveImages]:
                    cv.imwrite("./images/"+ location + "/image-left-" + str(i) + ".jpeg", phoneOne['img'])
                    cv.imwrite("./images/"+ location + "/image-right-" + str(i)+ ".jpeg", phoneTwo['img'])
                print(i)
                # sleep(3)

            cv.drawChessboardCorners(phoneOne['img'], (9,6), new_corners1, True)
            cv.drawChessboardCorners(phoneTwo['img'], (9,6), new_corners2, True)

        cv.imshow('phoneOneOne', phoneOne['img'])
        cv.imshow('phoneOneTwo', phoneTwo['img'])

        if cv.waitKey(1) & 0xFF == ord('q'):
            cv.destroyAllWindows()
            break
    return(objpoints, phoneOne['imgPoints'], phoneTwo['imgPoints'])

def saveSnapshot(): 
    phoneOne = {}
    phoneTwo = {}

    phoneOne['url']= URL['phoneOne']
    phoneTwo['url']= URL['phoneTwo']

    username = '123'
    password = '123'
        
    req1 = requests.get(phoneOne['url'], auth=(username, password)).content
    phoneOne['img'] = cv.imdecode(np.frombuffer(req1, np.uint8), -1)

    req2 = requests.get(phoneTwo['url'], auth=(username, password)).content
    phoneTwo['img'] = cv.imdecode(np.frombuffer(req2, np.uint8), -1)

    cv.imwrite("image-left.jpeg", phoneOne['img'])
    cv.imwrite("image-right.jpeg", phoneTwo['img'])

    while(True):
        cv.imshow("phoneTwoShot", phoneOne['img'])
        cv.imshow("phoneOneShot", phoneTwo['img'])
        if cv.waitKey(1) & 0xFF == ord('q'):
            cv.destroyAllWindows()
            break

if __name__ == "__main__": 
    
    phoneOne = {}
    phoneTwo = {}

    phoneOne['params'], phoneTwo['params'] = getCameraCalibration()

    [phoneOne['map1'], phoneOne['map2']], [phoneTwo['map1'], phoneTwo['map2']] = getStereoCalibration(phoneOne['params'], phoneTwo['params'])

    takeSnap = input("Take new Snapshots? Y/N: ")
    if ANS[takeSnap]:
        sleep(2)
        saveSnapshot()
        
    testImg1 = cv.imread("image-left.jpeg")
    testImg2 = cv.imread("image-right.jpeg")
    
    rectifiedImage1 = cv.remap(testImg1, phoneOne['map1'], phoneOne['map2'], cv.INTER_NEAREST)
    rectifiedImage2 = cv.remap(testImg2, phoneTwo['map1'], phoneTwo['map2'], cv.INTER_NEAREST)
   
    combinedImg = np.concatenate((rectifiedImage1, rectifiedImage2), axis= 1)

    while(True):
        cv.imshow("stereo", combinedImg)
        if cv.waitKey(1) & 0xFF == ord('q'):
            cv.destroyAllWindows()
            break
