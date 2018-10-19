import cwiid
import time
import json

def main():
    _ = raw_input('Press enter after pressing 1 + 2 on Wiimote\n')
    try:
        wii = cwiid.Wiimote()
    except(RuntimeError):
        print 'Failed to connect ... is Bluetooth on?'
    
    print 'Connection successful'

    # print initial state
    wii.rpt_mode = cwiid.RPT_ACC | cwiid.RPT_IR | cwiid.RPT_BTN
    time.sleep(1) # let the sensors wake up
    print 'Initial state:  ' + str(wii.state)

    with open('./data/example.json', 'w+') as f:
        f.write(json.dumps(wii.state, sort_keys=True, indent=4))

    return wii

def cleanup(wii):
    del wii
    print 'Wii disconnected'

if __name__ == "__main__":
    wii = main()
    cleanup(wii)
