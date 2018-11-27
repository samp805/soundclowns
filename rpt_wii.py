import cwiid
import time
import json
import pdb
import numpy as np
import cv2 as cv
import scipy.signal as sp
import scipy.stats as ss

xmax = 1024
ymax = 768
tolerance = 20

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

def calibrate(wii):
    print('Gently move around the Wiimote to find the center')
    center = (xmax/2, ymax/2)
    in_center = False
    close = False
    while(not in_center):
        current_state = wii.state
        try:
            xcoord = current_state['ir_src'][0]['pos'][0]
            ycoord = current_state['ir_src'][0]['pos'][1]
        except TypeError: # means you moved out of the frame
            continue
        in_center = (abs(xcoord - center[0]) < tolerance) and (abs(ycoord-center[1]) < tolerance)

    print('Found the center: {} ... stay there'.format(wii.state))
    return

def poll(wii):
    print('Hold B and make motion...')
    try:
        old_state = wii.state
        last_valid = (xmax/2, ymax/2)
        run = True
        while(run):
            wait_for_b_press(wii)
            b_pressed = (wii.state.get('buttons') == 4)
            while(b_pressed):
                current_state = wii.state
    
                if (old_state != current_state):
                    try:
                        xcoord = current_state['ir_src'][0]['pos'][0]
                        ycoord = current_state['ir_src'][0]['pos'][1]
                        last_valid = (xcoord, ycoord)
                        print('x:  {}, y:  {}'.format(xcoord, ycoord))
                    except TypeError:
                        # hitting this means you went out of frame somewhere
                        # your last valid coordinates will be xcoord & ycoord

                        if(abs(last_valid[0]-xmax) < tolerance): # close to right edge
                            print('right edge')
                        elif(last_valid[0] < tolerance): # close to left edge
                            print('left edge')
                        elif(abs(last_valid[1]-ymax) < tolerance): # close to top
                            print('top edge')
                        elif(last_valid[1] < tolerance): # bottom edge
                            print('bottom edge')
                        else:
                            print('error')
                    old_state = current_state

                b_pressed = (wii.state.get('buttons') == 4)


            run = (raw_input('Draw again? (y/n) ') == 'y')
    except(KeyboardInterrupt):
        print('Quitting...')

def cleanup(wii):
    del wii
    print 'Wii disconnected'

if __name__ == "__main__":
    wii = connect()
    calibrate(wii)
    poll(wii)
    cleanup(wii)
