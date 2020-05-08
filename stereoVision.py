import urllib.request
import cv2 as cv
from pickle import load
import numpy as np
import ipcamURLOpener
from tkinter import *
from threading import Thread
from functools import partial


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



def getStereoMapping():
    with open("./camera_params/phoneCamStereoMap", "rb") as file:
        phoneCamStereoMap = load(file)
    file.close()
    with open("./camera_params/webCamStereoMap", "rb") as file:
        webCamStereoMap = load(file)
    file.close()
    return(phoneCamStereoMap, webCamStereoMap)

def setValues(minDisp, numDisp, blockSize,uniquenessRatio,speckleWindowSize, speckleRange, disp12MaxDiff,preFilterCap, lmbda, sigma):
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


def displayDisparity(obj):
    stereo, wls_filter,min_disp, num_disp = obj
    stereo_criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    alpha = 0.1
    phonecam = {}
    webcam = {}

    [phonecam['map1'], phonecam['map2']], [webcam['map1'], webcam['map2']] = getStereoMapping()
      

    stereoR=cv.ximgproc.createRightMatcher(stereo) # Create another stereo for right this time

    url = ipcamURLOpener.url 
    webcamCap = cv.VideoCapture(0)
    webcamCap.set(cv.CAP_PROP_FRAME_WIDTH,1280)
    webcamCap.set(cv.CAP_PROP_FRAME_HEIGHT,720)

    
    kernel= np.ones((3,3),np.uint8)
    

    while True:
        # Start Reading Camera images
        req = urllib.request.urlopen(url)
        ret = webcamCap.grab()

        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        
        frameR = cv.imdecode(arr, -1)
        x, frameL  = webcamCap.retrieve()

        # Rectify the images on rotation and alignement
        Left_nice= cv.remap(frameL, webcam['map1'], webcam['map2'], cv.INTER_LANCZOS4, cv.BORDER_CONSTANT, 0)  # Rectify the image using the kalibration parameters founds during the initialisation
        Right_nice= cv.remap(frameR,phonecam['map1'], phonecam['map2'], cv.INTER_LANCZOS4, cv.BORDER_CONSTANT, 0)
        
        # Convert from color(BGR) to gray
        grayR= cv.cvtColor(Right_nice,cv.COLOR_BGR2GRAY)
        grayL= cv.cvtColor(Left_nice,cv.COLOR_BGR2GRAY)

        # Compute the 2 images for the Depth_image
        disp = stereo.compute(grayL,grayR)#.astype(np.float32)/ 16
        dispL= disp
        dispR= stereoR.compute(grayR,grayL)
        dispL= np.int16(dispL)
        dispR= np.int16(dispR)

        # Using the WLS filter
        filteredImg= wls_filter.filter(dispL,grayL,None,dispR)
        filteredImg = cv.normalize(src=filteredImg, dst=filteredImg, beta=0, alpha=255, norm_type=cv.NORM_MINMAX);
        filteredImg = np.uint8(filteredImg)

        #cv2.imshow('Disparity Map', filteredImg)
        disp= ((disp.astype(np.float32)/ 16)-min_disp)/num_disp 
        # Calculation allowing us to have 0 for the most distant object able to detect

        # Resize the image for faster executions
        # dispR= cv2.resize(disp,None,fx=0.7, fy=0.7, interpolation = cv2.INTER_AREA)

        # Filtering the Results with a closing filter
        closing= cv.morphologyEx(disp,cv.MORPH_CLOSE, kernel) 
        # Apply an morphological filter for closing little "black" holes in the picture(Remove noise) 

        # Colors map
        dispc= (closing-closing.min())*255
        dispC= dispc.astype(np.uint8)                                  
         # Convert the type of the matrix from float32 to uint8, this way you can show the results with the function cv2.imshow()
        disp_Color= cv.applyColorMap(dispC,cv.COLORMAP_OCEAN)         
        # Change the Color of the Picture into an Ocean Color_Map
        filt_Color= cv.applyColorMap(filteredImg,cv.COLORMAP_OCEAN) 

        # Show the result for the Depth_image
        #cv2.imshow('Disparity', disp)
        #cv2.imshow('Closing',closing)
        #cv2.imshow('Color Depth',disp_Color)
        cv.imshow('Filtered Color Depth',filt_Color)

        # Mouse click
        # cv.setMouseCallback("Filtered Color Depth",coords_mouse_disp,filt_Color)
        
        # End the Programme
        if cv.waitKey(1) & 0xFF == ord(' '):
            webcamCap.release()

            break
        
    # Save excel
    ##wb.save("data4.xlsx")

    # Release the Cameras
    cv.destroyAllWindows()
    
if __name__ == "__main__":
    root = tk.Tk()
    main = MainView(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_geometry("400x650")
    root.mainloop()