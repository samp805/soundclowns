#the next line is only needed for python2.x and not necessary for python3.x
#import pygame and libraries
from pygame.locals import *
from random import randrange
import os
import pygame
import pygameMenu
import cwiid
import time
import json
from pygameMenu.locals import *
import RPi.GPIO as GPIO
import serial
import math



POLL = pygame.USEREVENT

ABOUTUS = ['Matthew  Bell','Kyle  Bouwens','Timothy  Kennedy','Sam Peters']
chan_dict = {'right': 6, 'left':13, 'up':26, 'down':19}

COLOR_BACKGROUND = (128, 32, 128)
COLOR_BLACK = (0, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)
FPS = 30.0
MENU_BACKGROUND_COLOR = (228, 55, 36)
xmax = 1024
ymax = 768
tolerance = 30
PI = 3.14159265

GPIO.setmode(GPIO.BCM)
GPIO.setup(chan_dict.values(), GPIO.OUT)
GPIO.output(chan_dict['right'], GPIO.LOW)
GPIO.output(chan_dict['left'], GPIO.LOW)
GPIO.output(chan_dict['up'], GPIO.LOW)
GPIO.output(chan_dict['down'], GPIO.LOW)

pygame.init()
pygame.font.init()
    
# Create pygame screen and objects
surface = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
x = surface.get_width()
y = surface.get_height()
WINDOW_SIZE = (x,y)
pygame.display.set_caption('SoundClowns')
surface.fill(COLOR_BACKGROUND)
clock = pygame.time.Clock()
dt = 1 / FPS
myfont = pygame.font.Font(pygameMenu.fonts.FONT_BEBAS, 30)
startsurface = myfont.render('Press 1 + 2  on  Wiimote', False, (0,0,0))
surface.blit(startsurface,(x/2-x/4,y/2))
pygame.display.update()
try:
    wiimote = cwiid.Wiimote()
except(RuntimeError):
    surface.fill(COLOR_BACKGROUND)
    failsurface = myfont.render('Failed  to  connect ...  is  Bluetooth  on?', False, (0,0,0))
    surface.blit(failsurface,(x/2-x/4,y/2))
    pygame.display.update()
    time.sleep(5)
    raise # so the program will exit if we can't connect
successsurface = myfont.render('Connection  Successful', False, (0,0,0))
wiimote.rumble = 1
time.sleep(0.5)
wiimote.rumble = 0
surface.blit(successsurface,(x/2-x/4,y/2+y/4))
pygame.display.update()

# open serial connection
try:
    ser = serial.Serial('/dev/ttyUSB0',
                        baudrate=115200,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        write_timeout=3) # hopefully this stays constant but it might not
except serial.serialutil.SerialException:
    badserial = myfont.render('Could not open serial connection ... Quitting', False, (0,0,0))
    surface.blit(badserial, (x/2-x/4, y/2+y/4))
    pygame.display.update()
    time.sleep(3)
    raise


wiimote.rpt_mode = cwiid.RPT_ACC | cwiid.RPT_IR | cwiid.RPT_BTN
wiimote.led = 1

# -----------------------------------------------------------------------------

def main_background():
    """
    Function used by menus, draw on background while menu is active.

    :return: None
    """
    surface.fill(COLOR_BACKGROUND)

# -----------------------------------------------------------------------------
def list_edges():
    topedge = myfont.render('Distortion', False, (0,0,0))
    bottomedge = myfont.render('Stereo  Reverb', False, (0,0,0))
    leftedge = myfont.render('Delay  Left  Speaker', False, (0,0,0))
    rightedge = myfont.render('Delay  Right  Speaker',False, (0,0,0))
    surface.blit(topedge,(x/2,0))
    surface.blit(bottomedge,(x/2,15*y/16))
    surface.blit(leftedge,(0,y/2))
    surface.blit(rightedge,(7*x/8,y/2))
    pygame.display.update()
    return

def wait_for_b_press(wii):
    while(True):
        if (wii.state['buttons'] == 4):
            return True

def calibrate(wii):
    calibratemessage = myfont.render('Gently  move  the  Wiimote  to  find  the  center', False, (0,0,0))
    surface.blit(calibratemessage,(x/2-x/4,y/2))
    pygame.display.update()
    center = (xmax/2, ymax/2)
    in_center = False
    while(not in_center):
        current_state = wii.state
        try:
            xcoord = current_state['ir_src'][0]['pos'][0]
            ycoord = current_state['ir_src'][0]['pos'][1]
        except TypeError: # means you moved out of the frame
            continue
        in_center = (abs(xcoord - center[0]) < tolerance) and (abs(ycoord-center[1]) < tolerance)
    surface.fill(COLOR_BACKGROUND)
    foundcenter = 'Found  the  center:  X:{}  ,Y:{}  ...  stay  there'.format(xcoord,ycoord)
    centermessage = myfont.render(foundcenter, False, (0,0,0))
    surface.blit(centermessage,(x/2-x/4,y/2+y/4))
    pygame.draw.circle(surface, COLOR_GREEN, (x/2, y/2), 50, 0)
    pygame.display.update()
    wii.rumble = 1
    time.sleep(0.5)
    wii.rumble = 0
    return 

def calc_roll(state):
    a_x = state['acc'][0] - 125
    a_y = state['acc'][1] - 126
    a_z = state['acc'][2] - 151
    roll = math.atan2(a_x,a_z) if a_z != 0 else PI/2
    roll = roll - PI/2 if roll > 0 else roll + PI/2
    roll /= PI/2
    roll += 1
    roll /= 2
    return roll * 100

def modulate_effect(state):
    data = calc_roll(state)
    ser.write(str(data))

def wiidata(wm):
    """
    Function used to get wiimote data and write as to json
    :param wmstate: wiimote state dictionary
    :return: None
    """

    main_menu.disable()
    main_menu.reset(1)
    bg_color = COLOR_BACKGROUND
    surface.fill(bg_color)
    # have the user find the center
    calibrate(wm)
    
    #KYLE: let the user know it's been calibrated
    old_state = wm.state
    effect_on = False
    while True:

        # Clock tick
        clock.tick(30)
        
        # Application events
        button = wm.state.get('buttons')
        pygame.event.post(pygame.event.Event(POLL)) 
        wmevents = pygame.event.get()
        for e in wmevents:
            pygame.event.post(pygame.event.Event(POLL))
            if e.type == QUIT:
                exit()
            elif e.type == KEYDOWN  :
                if e.key == K_ESCAPE and main_menu.is_disabled():
                    main_menu.enable()
                    return
            elif e.type == POLL:
                surface.fill(bg_color)
                bmessage = 'Press  and  Hold  B  to  get  sound'
                bsurface = myfont.render(bmessage, False,(0,0,0))
                list_edges()
                try:
                    old_state = wm.state
                    last_valid = (xmax/2, ymax/2)
                    run = True
                    while(run):
                        button = wm.state.get('buttons')
                        # wait_for_b_press(wm)
                        while(button == 4): # while b is pressed
                            current_state = wm.state
                            if(effect_on):
                                modulate_effect(current_state)
                            surface.fill(bg_color)
                            if (old_state != current_state):
                                try:
                                    xcoord = current_state['ir_src'][0]['pos'][0]
                                    ycoord = current_state['ir_src'][0]['pos'][1]
                                    last_valid = (xcoord, ycoord)
                                    position = 'x: {}, y: {}'.format(xcoord, ycoord)
                                    positionmessage = myfont.render(position, False, (0,0,0))
                                    surface.blit(positionmessage,(x/2-x/4,y/2))
                                    pygame.display.update()
                                    list_edges()
                                except TypeError:
                                    # hitting this means you went out of frame somewhere
                                    # your last valid coordinates will be xcoord & ycoord
                                    surface.fill(bg_color)
                                    list_edges()
                                    if(abs(last_valid[0]-xmax) < tolerance): # close to right edge
                                        leftedge = myfont.render('Delay  Left  Speaker',False, COLOR_GREEN)
                                        surface.blit(leftedge, (0,y/2))
                                        #GPIO.output(chan_dict['up'], GPIO.LOW)
                                        #GPIO.output(chan_dict['down'], GPIO.LOW)
                                        #GPIO.output(chan_dict['left'], GPIO.LOW)
                                        GPIO.output(chan_dict['left'], GPIO.HIGH)
                                        effect_on = True
                                    elif(last_valid[0] < tolerance): # close to left edge
                                        rightedge = myfont.render('Delay  Right  Speaker',False, COLOR_GREEN)
                                        surface.blit(rightedge, (7*x/8,y/2))
                                        #GPIO.output(chan_dict['up'], GPIO.LOW)
                                        #GPIO.output(chan_dict['down'], GPIO.LOW)
                                        #GPIO.output(chan_dict['right'], GPIO.LOW)
                                        GPIO.output(chan_dict['right'], GPIO.HIGH)
                                        effect_on = True
                                    elif(abs(last_valid[1]-ymax) < tolerance): # close to top
                                        bottomedge = myfont.render('Stereo  Reverb',False, COLOR_GREEN)
                                        surface.blit(bottomedge,(x/2,15*y/16))
                                        #GPIO.output(chan_dict['left'], GPIO.LOW)
                                        #GPIO.output(chan_dict['down'], GPIO.LOW)
                                        #GPIO.output(chan_dict['right'], GPIO.LOW)
                                        GPIO.output(chan_dict['down'], GPIO.HIGH)
                                        effect_on = True
                                    elif(last_valid[1] < tolerance): # bottom edge 
                                        topedge = myfont.render('Distortion',False, COLOR_GREEN)
                                        surface.blit(topedge,(x/2,0))
                                        #GPIO.output(chan_dict['up'], GPIO.LOW)
                                        #GPIO.output(chan_dict['left'], GPIO.LOW)
                                        #GPIO.output(chan_dict['right'], GPIO.LOW)
                                        GPIO.output(chan_dict['up'], GPIO.HIGH)
                                        effect_on = True
                                    else:
                                        # just ignore it in this case actually
                                        pass
                                    pygame.display.update()
                                old_state = current_state
                            
                            button = wm.state.get('buttons')
                        
                        list_edges()
                        surface.blit(bsurface,(x/2-x/4,y/2-y/4))
                        pygame.display.update()
                        
                        if button == 128 and main_menu.is_disabled():
                            main_menu.enable()
                            return
                        elif button == 16: # minus button will clear effects
                            surface.fill(bg_color)
                            cleared = myfont.render('Cleared  Effects',False, (0,0,0))
                            surface.blit(cleared, (x/2-x/4,y/2))
                            pygame.display.update()
                            GPIO.output(chan_dict['up'], GPIO.LOW)
                            GPIO.output(chan_dict['left'], GPIO.LOW)
                            GPIO.output(chan_dict['right'], GPIO.LOW)
                            GPIO.output(chan_dict['down'], GPIO.LOW)
                            effect_on = False

                        else:
                            pygame.display.flip()
                            pygame.event.clear(POLL)

                except KeyboardInterrupt:
                    print('Quitting') # Kyle: Replace with UI message
                    pass

                # Pass events to main_menu
		surface.fill(bg_color)
		pygame.display.flip()

# -----------------------------------------------------------------------------
# ABOUT US MENU
about_us_menu = pygameMenu.TextMenu(surface,
                                 bgfun=main_background,
                                 color_selected=COLOR_WHITE,
                                 font=pygameMenu.fonts.FONT_BEBAS,
                                 font_color=COLOR_BLACK,
                                 font_size_title=30,
                                 font_title=pygameMenu.fonts.FONT_8BIT,
                                 menu_color=MENU_BACKGROUND_COLOR,
                                 menu_color_title=COLOR_WHITE,
                                 menu_height=int(WINDOW_SIZE[1] * 0.6),
                                 menu_width=int(WINDOW_SIZE[0] * 0.6),
                                 onclose=PYGAME_MENU_DISABLE_CLOSE,
                                 option_shadow=False,
                                 joystick_enabled= True,
                                 text_color=COLOR_BLACK,
                                 text_fontsize=20,
                                 title='The Sound Clowns',
                                 window_height=WINDOW_SIZE[1],
                                 window_width=WINDOW_SIZE[0]
                                 )
for m in ABOUTUS:
    about_us_menu.add_line(m)
about_us_menu.add_line(PYGAMEMENU_TEXT_NEWLINE)
about_us_menu.add_option('Return  to  menu', PYGAME_MENU_BACK)

# MAIN MENU
main_menu = pygameMenu.Menu(surface,
                            bgfun=main_background,
                            color_selected=COLOR_WHITE,
                            font=pygameMenu.fonts.FONT_BEBAS,
                            font_color=COLOR_BLACK,
                            font_size=30,
                            menu_alpha=100,
                            menu_color=MENU_BACKGROUND_COLOR,
                            menu_height=int(WINDOW_SIZE[1] * 0.6),
                            menu_width=int(WINDOW_SIZE[0] * 0.6),
                            onclose=PYGAME_MENU_DISABLE_CLOSE,
                            option_shadow=False,
                            joystick_enabled= True,
                            title='Sound  Clowns',
                            window_height=WINDOW_SIZE[1],
                            window_width=WINDOW_SIZE[0],
                            wiimote=wiimote
                            )

main_menu.add_option('Start', wiidata, wiimote)
main_menu.add_option('About  Us', about_us_menu)
main_menu.add_option('Quit', PYGAME_MENU_EXIT)

# -----------------------------------------------------------------------------


# Main loop
while True:

    # Tick
    clock.tick(30)

    # Application events
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            exit()

    # Main menu
    main_menu.mainloop(events)

    # Flip surface
    pygame.display.flip()
