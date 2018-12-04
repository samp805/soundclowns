import cwiid
import time
import json
import math

PI = 3.1459
ACC_MAX = 255.0
g = 9.807

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
    wii.led = 1
    time.sleep(1) # let the sensors wake up
    print 'Initial state:  ' + str(wii.state)

    return wii


def poll(wii):
    try:
        old_state = wii.state
        t0 = time.time()
        while(True):
            
            b_pressed = (wii.state.get('buttons') == 4)
            current_state = wii.state
            if b_pressed and (old_state != current_state):
                a_x = current_state['acc'][0] - 125
                a_y = current_state['acc'][1] - 126
                a_z = current_state['acc'][2] - 151

                roll = math.atan2(a_x,a_z) if a_z != 0 else PI/2
                roll = roll - PI/2 if roll > 0 else roll + PI/2
                roll /= PI/2
                roll += 1
                roll /= 2

                print('(x,y,z): ({},{},{}) || roll: {}'.format(a_x,a_y,a_z,roll))



                old_state = current_state
    except(KeyboardInterrupt):
        print('Quitting...')

def cleanup(wii):
    del wii
    print 'Wii disconnected'

if __name__ == "__main__":
    wii = connect()
    poll(wii)
    cleanup(wii)
