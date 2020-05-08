import cv2
import numpy as np
from matplotlib import pyplot as plt

img = cv2.imread('image1.jpeg')

# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

edges = cv2.Canny(img,100,200)

while True:
    cv2.imshow("Img",edges)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break