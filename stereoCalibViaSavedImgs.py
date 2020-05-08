import cv2 as cv
import numpy as np
import glob
import pickle

IMAGE_SIZE = (1280, 720)
ALPHA = 0.25

ANS = {"y": True,
    "Y": True,
    "N": False,
    "n": False}

recalc = input("Recalculate points from images? Y/N: ")

if ANS[recalc]:
    # termination criteria
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((6*9,3), np.float32)

    objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)
    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space

    imgpoints1 = [] # 2d points in image plane.
    imgpoints2 = [] # 2d points in image plane.

    images2 = glob.glob('./images/stereoCamCalibPoints/image-left-*.jpeg')
    images1 = glob.glob('./images/stereoCamCalibPoints/image-right-*.jpeg')
    i = 0
    for fname1, fname2 in zip(images1,images2):
        img1 = cv.imread(fname1)
        img2 = cv.imread(fname2)

        gray1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)
        gray2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)

        ret1, corners1 = cv.findChessboardCorners(gray1, (9,6), None)
        ret2, corners2 = cv.findChessboardCorners(gray2, (9,6), None)

        if ret1 and ret2:
            i = i + 1
            objpoints.append(objp)
            new_corners1 = cv.cornerSubPix(gray1, corners1, (11,11), (-1,-1), criteria)
            new_corners2 = cv.cornerSubPix(gray2, corners2, (11,11), (-1,-1), criteria)
            imgpoints1.append(new_corners1)
            imgpoints2.append(new_corners2)
            print(i)
            # cv.drawChessboardCorners(img1, (9,6), corners2, ret1)
            # cv.imshow('img1', img1)
            # cv.waitKey(250)


    with open("./camera_params/phoneOneParams", "rb") as file:
        phoneOnePara = pickle.load(file)
    file.close()
    with open("./camera_params/phoneTwoParams", "rb") as file:
        phoneTwoPara = pickle.load(file)
    file.close()

    stereo_criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    phoneOne = {}
    phoneTwo = {}
    ret , phoneOne['camMtx'], phoneOne['distMtx'], phoneOne['rotMtx'], phoneOne['trnsMrx'] = phoneOnePara
    ret , phoneTwo['camMtx'], phoneTwo['distMtx'], phoneTwo['rotMtx'], phoneTwo['trnsMrx'] = phoneTwoPara

    phoneOne['optCamMtx'], phoneOne['roi'] = cv.getOptimalNewCameraMatrix(
        phoneOne['camMtx'], 
        phoneOne['distMtx'], 
        IMAGE_SIZE, 
        alpha = ALPHA)

    phoneTwo['optCamMtx'], phoneTwo['roi'] = cv.getOptimalNewCameraMatrix(
        phoneTwo['camMtx'], 
        phoneTwo['distMtx'], 
        IMAGE_SIZE, 
        alpha = ALPHA)

    ret, _ , _ , _ , _ , rotMtx, trnsMtx, _ , _ = cv.stereoCalibrate(
        objpoints,
        imgpoints1, 
        imgpoints2, 
        phoneTwo['optCamMtx'], 
        phoneTwo['distMtx'], 
        phoneOne['optCamMtx'], 
        phoneOne['distMtx'], 
        IMAGE_SIZE)

    phoneTwo['stereoRectRotMtx'], phoneOne['stereoRectRotMtx'], phoneTwo['projMtx'], phoneOne['projMtx'], Q , phoneTwo['stereoROI'] , _ = cv.stereoRectify(
        phoneTwo['camMtx'],
        phoneTwo['distMtx'],
        phoneOne['camMtx'],
        phoneOne['distMtx'],
        IMAGE_SIZE, 
        rotMtx, 
        trnsMtx,
        # flags= cv.CALIB_ZERO_DISPARITY, 
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
else:
    with open("./camera_params/phoneOneStereoMap", "rb") as file:
        phoneOneStereoMap = pickle.load(file)
    file.close()
    with open("./camera_params/phoneTwoStereoMap", "rb") as file:
        phoneTwoStereoMap = pickle.load(file)
    file.close()

phoneOne = {}
phoneTwo = {}

phoneOne['map1'], phoneOne['map2'] = phoneOneStereoMap
phoneTwo['map1'], phoneTwo['map2'] = phoneTwoStereoMap

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
