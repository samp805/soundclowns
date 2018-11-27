import cwiid
import time
import json
import pdb
import numpy as np
import cv2 as cv
import scipy.signal as sp
import scipy.stats as ss

xsize = 1024
ysize = 768
x, y = np.indices((xsize, ysize))
xcenter = xsize/2
ycenter = ysize/2
radius = 20
circle = (x - xcenter)**2 + (y - ycenter)**2 < radius**2
dim = (xsize,ysize)
kernel = np.ones((5,5),np.uint8)


def connect():
    _ = raw_input('Press enter after pressing 1 + 2 on Wiimote\n')
    try:
        wii = cwiid.Wiimote()
    except(RuntimeError):
        print 'Failed to connect ... is Bluetooth on?'
        raise
    
    print 'Connection successful'

    # print initial state
    wii.rpt_mode = cwiid.RPT_ACC | cwiid.RPT_IR | cwiid.RPT_BTN
    time.sleep(1) # let the sensors wake up

    return wii

def wait_for_b_press(wii):
    while(True):
        if (wii.state['buttons'] == 4):
            return True

def poll(wii):
    print('Hold B and draw a circle...')
    try:
        old_state = wii.state
        run = True
        while(run):
            map = np.zeros(dim)
            wait_for_b_press(wii)
            b_pressed = (wii.state.get('buttons') == 4)
            while(b_pressed):
                current_state = wii.state
    
                if (old_state != current_state):
                    old_state = current_state
                    try:
                        xcoord = current_state['ir_src'][0]['pos'][0]
                        ycoord = current_state['ir_src'][0]['pos'][1]
                        print('x: {} || y: {}'.format(xcoord,ycoord))
                        map[xcoord,ycoord] = 1
                    except TypeError:
                        print('state:  {}'.format(wii.state))
                        print('Warning: Out of frame')
                b_pressed = (wii.state.get('buttons') == 4)

            #pdb.set_trace()
            closed = cv.morphologyEx(map, cv.MORPH_CLOSE, kernel)
            print('here')
            #result = sp.correlate2d(closed, circle, mode='valid') / 30000.0
            result = ss.pearsonr(closed.flatten(), circle.flatten())
            print(result)
            run = (raw_input('Draw again? (y/n) ') == 'y')
    except(KeyboardInterrupt):
        print('Quitting...')

def cleanup(wii):
    del wii
    print 'Wii disconnected'

if __name__ == "__main__":
    wii = connect()
    poll(wii)
    cleanup(wii)
