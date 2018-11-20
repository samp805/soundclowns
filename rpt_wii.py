import cwiid
import time
import json
import pygame
import pygameMenu

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
    print 'Initial state:  ' + str(wii.state)
    wii.led = 1

    with open('./data/example.json', 'w+') as f:
        f.write(json.dumps(wii.state, sort_keys=True, indent=4))

    return wii

def report(state):
    with open('data.json', 'a+') as f:
        f.write(json.dumps(state.get('ir_src')) + '\n')

def poll(wii):
    try:
        old_state = wii.state
        while(True):
            current_state = wii.state
            if (old_state != current_state):
                report(wii.state)
                # print(wii.state)
                old_state = current_state
    except(KeyboardInterrupt):
        print('Quitting...')
        


def cleanup(wii):
    del wii
    print 'Wii disconnected'


