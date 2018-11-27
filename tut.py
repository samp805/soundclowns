import numpy as np
import cv2 as cv
import scipy as sp
import cwiid

size = 1024
x, y = np.indices((size, size))
center = size/2
radius = size/4
circle = (x - center)**2 + (y - center)**2 < radius**2

dim = (size,size)
map = np.zeros(dim)
kernel = np.ones((5,5),np.uint8)
circle = (x-size/2)**2 + y(-size/2)**2 < radius**2

xcoord = state.get('ir_src')[0]['pos'][0]
ycoord = state.get('ir_src')[0]['pos'][1]
    
closed = cv.morphologyEx(map, cv.MORPH_CLOSE, kernel)


result = sp.signal.correlate2d(closed, circle)
print(result)