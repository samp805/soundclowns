import cwiid
import time
import json


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

    with open('./data/example.json', 'w+') as f:
        f.write(json.dumps(wii.state, sort_keys=True, indent=4))

    return wii


def poll(wii):
    try:
        old_state = wii.state
        t0 = time.time()
        while(True):
            b_pressed = (wii.state.get('buttons') == 4)
            current_state = wii.state
            if b_pressed and (old_state != current_state):
                print(wii.state)
                old_state = current_state
                dt = time.time() - t0
                t0 = time.time()
                print(dt)
    except(KeyboardInterrupt):
        print('Quitting...')

def cleanup(wii):
    del wii
    print 'Wii disconnected'

if __name__ == "__main__":
    wii = connect()
    poll(wii)
    cleanup(wii)
