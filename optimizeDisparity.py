# Package importation
import os
import pickle
import time
import tkinter as tk
import urllib.request
from functools import partial
from multiprocessing import Pool
from threading import Thread

import cv2
import numpy as np

import ipcamURLOpener


class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
    def show(self):
        self.lift()

class Page1(Page):
    def __init__(self, *args, **kwargs):

        Page.__init__(self, *args, **kwargs)
        
        self.minDisp = tk.IntVar()
        scale = tk.Scale(self, orient=tk.HORIZONTAL, length=300,
                                from_=0, to=15, tickinterval=1, resolution=1, variable=self.minDisp, label="minDisp", command= self._on_scale)
        scale.pack()
        self.minDisp.set(5)

        self.numDisp = tk.IntVar()
        self.scale2 = tk.Scale(self, orient=tk.HORIZONTAL, length=300,
                                from_=1, to=200, tickinterval=10, resolution=16, variable=self.numDisp, label="numDisp")
        self.scale2.pack()
        self.numDisp.set(128)


        self.blockSize = tk.IntVar()
        scale3 = tk.Scale(self, orient=tk.HORIZONTAL, length=300,
                                from_=3, to=15, tickinterval=2, resolution=1, variable=self.blockSize, label="blockSize (Only pick Odd value)")
        scale3.pack()
        self.blockSize.set(5)


        self.speckleWindowSize  = tk.IntVar()
        self.speckleWindowSize.set(100)

        scale4 = tk.Scale(self, orient=tk.HORIZONTAL, length=300,
                                from_=50, to=250, tickinterval=25, resolution=5, variable=self.speckleWindowSize, label="speckleWindowSize" )
        scale4.pack()

        self.speckleRange  = tk.IntVar()
        scale5 = tk.Scale(self, orient=tk.HORIZONTAL, length=300,
                                from_=0, to=40, tickinterval=5, resolution=1, variable=self.speckleRange , label="speckleRange")
        scale5.pack()
        self.speckleRange.set(32)

        self.disp12MaxDiff  = tk.IntVar()
        scale6 = tk.Scale(self, orient=tk.HORIZONTAL, length=300,
                                from_=-1, to=10, tickinterval=1, resolution=1, variable=self.disp12MaxDiff , label="disp12MaxDiff")
        scale6.pack()
        self.disp12MaxDiff.set(5)

        self.uniquenessRatio   = tk.IntVar()
        scale7 = tk.Scale(self, orient=tk.HORIZONTAL, length=300,
                                from_=0, to=20, tickinterval=2, resolution=1, variable=self.uniquenessRatio  , label="uniquenessRatio ")
        scale7.pack()
        self.uniquenessRatio.set(10)

        self.preFilterCap   = tk.IntVar()
        scale8 = tk.Scale(self, orient=tk.HORIZONTAL, length=300,
                                from_=0, to=10, tickinterval=10, resolution=1, variable=self.preFilterCap  , label="preFilterCap ")
        scale8.pack()
        self.preFilterCap.set(5)
        
    
    def _on_scale(self, value):
        value = int(value)
        self.scale2.configure(from_ = value, to = value + 160)

    def getValues(self):
        return([self.minDisp, 
        self.numDisp, 
        self.blockSize, 
        self.uniquenessRatio,
        self.speckleWindowSize, 
        self.speckleRange, 
        self.disp12MaxDiff,
        self.preFilterCap])


class Page2(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        self.sigma = tk.DoubleVar()
        scale = tk.Scale(self, orient=tk.HORIZONTAL, length=300,
                                from_=0.8, to=2.0, tickinterval=0.4, resolution=0.2, variable=self.sigma, label="Sigma")
        scale.pack()

        self.lmbda = tk.IntVar()
        scale2 = tk.Scale(self, orient=tk.HORIZONTAL, length=300,
                                from_=8000, to=80000, tickinterval=20000, resolution=1000, variable=self.lmbda, label="Lambda")
        scale2.pack()

    def getValues(self):
        return([self.lmbda, self.sigma])

class MainView(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        p1 = Page1(self)
        p2 = Page2(self)

        buttonframe = tk.Frame(self)
        container = tk.Frame(self)
        buttonframe.pack(side="top", fill="x", expand=False)
        container.pack(side="top", fill="both", expand=True)

        p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        val1, val2,val3,val4,val5,val6, val7, val8 = p1.getValues()
        val9,val10 = p2.getValues()
        set_values_loaded = partial(setValues, val1, val2, val3, val4, val5, val6, val7, val8, val9, val10)

        b1 = tk.Button(buttonframe, text="SGMB", command=p1.lift)
        b2 = tk.Button(buttonframe, text="Matcher", command=p2.lift)
        b3 = tk.Button(buttonframe, text="Apply values", command=set_values_loaded)


        b1.pack(side="left")
        b2.pack(side="left")
        b3.pack(side="right")

        p1.show()


# =========================sub Process===========================

def setValues(minDisp, numDisp, blockSize,uniquenessRatio,speckleWindowSize, speckleRange, disp12MaxDiff,preFilterCap, lmbda, sigma):
    print(1)

    stereo = cv2.StereoSGBM_create(minDisparity = minDisp.get(),
        numDisparities = numDisp.get(),
        blockSize = blockSize.get(),
        uniquenessRatio = uniquenessRatio.get(),
        speckleWindowSize = speckleWindowSize.get(),
        speckleRange = speckleRange.get(),
        disp12MaxDiff = disp12MaxDiff.get(),
        preFilterCap = preFilterCap.get(),
        P1 = 8*3*blockSize.get()**2,
        P2 = 32*3*blockSize.get()**2)

    wls_filter = cv2.ximgproc.createDisparityWLSFilter(matcher_left=stereo)
    wls_filter.setLambda(lmbda.get())
    wls_filter.setSigmaColor(sigma.get())
    
    t1 = Thread(target=displayDisparity, args=((stereo,wls_filter,numDisp.get(),minDisp.get()),))
    t1.daemon = True
    t1.start()


def coords_mouse_disp(event,x,y,flags,param):
    filt, disp = param
    if event == cv2.EVENT_LBUTTONDBLCLK:
        #print x,y,disp[y,x],filteredImg[y,x]
        """
				p p p
				p p p
				p p p
        """
        average=0
        for u in range (-1,2):     # (-1 0 1)
            for v in range (-1,2): # (-1 0 1)
                average += disp[y+u,x+v]
        average=average/9
        print('Average: '+ str(average))

#*************************************************
#***** Parameters for Distortion Calibration *****
#*************************************************

def displayDisparity(obj):
    stereo, wls_filter,min_disp, num_disp = obj
    
    flags = 0
    flags |= cv2.CALIB_FIX_INTRINSIC

    with open("./camera_params/phoneCamStereoMap", "rb") as file:
        Right_Stereo_Map = pickle.load(file)
    file.close()
    with open("./camera_params/webCamStereoMap", "rb") as file:
        Left_Stereo_Map = pickle.load(file)
    file.close()

    stereoR=cv2.ximgproc.createRightMatcher(stereo) # Create another stereo for right this time

    frameR = cv2.imread("image1.jpeg")
    frameL = cv2.imread("image2.jpeg")

    while True:
        
        # Rectify the images on rotation and alignement
        # Rectify the image using the calibration parameters founds during the initialisation
        Left_nice= cv2.remap(frameL,Left_Stereo_Map[0],Left_Stereo_Map[1], cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)  
        Right_nice= cv2.remap(frameR,Right_Stereo_Map[0],Right_Stereo_Map[1], cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)

        # Convert from color(BGR) to gray
        # grayR= cv2.cvtColor(Right_nice,cv2.COLOR_BGR2GRAY)
        # grayL= cv2.cvtColor(Left_nice,cv2.COLOR_BGR2GRAY)


        grayR= Right_nice
        grayL= Left_nice
        #=======================================================================================
        
        # Compute the 2 images for the Depth_image
        # Run the pool in multiprocessing
        st1 = (grayL,grayR,1 )
        st2 = (grayL,grayR,2 )

        # Computo para el stereo
        disp= stereo.compute(grayL,grayR)
        dispR= stereoR.compute(grayR,grayL)
        
        dispL= disp

        #=======================================================================================
    
        dispL= np.int16(dispL)
        dispR= np.int16(dispR)
        

        # Using the WLS filter
        filteredImg= wls_filter.filter(dispL,grayL,None,dispR)
        filteredImg = cv2.normalize(src=filteredImg, dst=filteredImg, beta=0, alpha=255, norm_type=cv2.NORM_MINMAX);
        filteredImg = np.uint8(filteredImg)

        # Change the Color of the Picture into an Ocean Color_Map
        filt_Color= cv2.applyColorMap(filteredImg,cv2.COLORMAP_OCEAN) 

        cv2.imshow('Filtered Color Depth',filt_Color)

        # Draw Red lines
        # for line in range(0, int(Right_nice.shape[0]/20)): # Draw the Lines on the images Then numer of line is defines by the image Size/20
        #     Left_nice[line*20,:]= (0,0,255)
        #     Right_nice[line*20,:]= (0,0,255)
    
        # cv2.imshow('Both Images', np.hstack([Left_nice, Right_nice]))
        
        # Mouse click
        cv2.setMouseCallback("Filtered Color Depth",coords_mouse_disp,(filt_Color,disp))
        
        #
            # End the Programme
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

        
    cv2.destroyAllWindows()


if __name__ == "__main__":
    root = tk.Tk()
    main = MainView(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_geometry("400x650")
    root.mainloop()
