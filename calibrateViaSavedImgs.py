import cv2 as cv
import numpy as np
import glob
import pickle

IMAGE_SIZE = (1280, 720)

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

    images1 = glob.glob('./images/camCalibPoints/image-left-*.jpeg')
    images2 = glob.glob('./images/camCalibPoints/image-right-*.jpeg')
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
            
    saveCamPara = input("Do you want to save cam Parameters? Y/N: ")
    if ANS[saveCamPara]:
        phoneOnePara = cv.calibrateCamera(objpoints, imgpoints1, gray1.shape[::-1], None, None)
        phoneTwoPara = cv.calibrateCamera(objpoints, imgpoints2, gray1.shape[::-1], None, None)
        with open("./camera_params/phoneOneParams", "wb") as file:
            pickle.dump(phoneOnePara, file)
        file.close()
        with open("./camera_params/phoneTwoParams", "wb") as file:
            pickle.dump(phoneTwoPara, file)
        file.close()
else:
    with open("./camera_params/phoneOneParams", "rb") as file:
        phoneOnePara = pickle.load(file)
    file.close()
    with open("./camera_params/phoneTwoParams", "rb") as file:
        phoneTwoPara = pickle.load(file)
    file.close()

testImg1 = cv.imread("image-left.jpeg")
testImg2 = cv.imread("image-right.jpeg")

_, crmx1, dist1, R1, _ = phoneOnePara
_, crmx2, dist2, R2, _ = phoneTwoPara

img1 = cv.undistort(testImg1, crmx1, dist1)
img2 = cv.undistort(testImg2, crmx2, dist2)

while(True):
    cv.imshow("phoneTwoShot", img1)
    cv.imshow("phoneOneShot", img2)
    if cv.waitKey(1) & 0xFF == ord('q'):
        cv.destroyAllWindows()
        break