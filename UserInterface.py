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
chan_dict = {'chorus': 6, 'base_delay':13, 'trigger_delay':5, 'distortion':26, 'reverb':19}

COLOR_BACKGROUND = (128, 128, 210)
COLOR_BLACK = (0, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)
FPS = 30.0
MENU_BACKGROUND_COLOR = (220, 180, 0)
xmax = 1024
ymax = 768
tolerance = 30
PI = 3.14159265

GPIO.setmode(GPIO.BCM)
GPIO.setup(chan_dict.values(), GPIO.OUT)
GPIO.output(chan_dict['chorus'], GPIO.LOW)
GPIO.output(chan_dict['base_delay'], GPIO.LOW)
GPIO.output(chan_dict['trigger_delay'], GPIO.LOW)
GPIO.output(chan_dict['distortion'], GPIO.LOW)
GPIO.output(chan_dict['reverb'], GPIO.LOW)

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
myfont2 = pygame.font.Font(pygameMenu.fonts.FONT_BEBAS, 60)
startsurface = myfont2.render('Press 1 + 2  on  Wiimote', False, (0,0,0))
startrect = startsurface.get_rect(center=(x/2,y/2))
surface.blit(startsurface,startrect)
pygame.display.update()
try:
    wiimote = cwiid.Wiimote()
except(RuntimeError):
    surface.fill(COLOR_BACKGROUND)
    failsurface = myfont.render('Failed  to  connect ...  is  Bluetooth  on?', False, (0,0,0))
    failrect = failsurface.get_rect(center=(x/2,y/2))
    surface.blit(failsurface,failrect)
    pygame.display.update()
    time.sleep(5)
    raise # so the program will exit if we can't connect
successsurface = myfont.render('Connection  Successful', False, (0,0,0))
successrect = successsurface.get_rect(center=(x/2,y/2+y/4))
wiimote.rumble = 1
time.sleep(0.5)
wiimote.rumble = 0
surface.blit(successsurface,successrect)
pygame.display.update()

# open serial connection
try:
    ser = serial.Serial('/dev/ttyUSB0',
                        baudrate=115200,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        write_timeout=3) # hopefully this stays constant but it might not
    ser.close()
    ser.open()
except serial.serialutil.SerialException:
    surface.fill(COLOR_BACKGROUND)
    badserial = myfont.render('Could not open serial connection ... Quitting', False, (0,0,0))
    badrect = badserial.get_rect(center = (x/2,y/2))
    surface.blit(badserial, badrect)
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
    topedge = myfont.render('Distortion', False, COLOR_RED)
    toprect = topedge.get_rect(center=(x/2,y/16))
    bottomedge = myfont.render('Stereo  Reverb', False, COLOR_RED)
    bottomrect = bottomedge.get_rect(center=(x/2,15*y/16))
    leftedge = myfont.render('Delay', False, COLOR_RED)
    rightedge = myfont.render('Tremolo',False, COLOR_RED)
    surface.blit(topedge,toprect)
    surface.blit(bottomedge,bottomrect)
    surface.blit(leftedge,(x/16,y/2))
    surface.blit(rightedge,(13*x/16,y/2))
    pygame.display.update()
    return

def wait_for_b_press(wii):
    while(True):
        if (wii.state['buttons'] == 4):
            return True

def calibrate(wii):
    calibratemessage = myfont.render('Gently  move  the  Wiimote  to  find  the  center', False, (0,0,0))
    calirect = calibratemessage.get_rect(center=(x/2,y/2))
    surface.blit(calibratemessage,calirect)
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
    centrect = centermessage.get_rect(center=(x/2,y/2+y/4))
    surface.blit(centermessage,centrect)
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
    ser.write(str(int(data)).encode())
    ser.flush()

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
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE and main_menu.is_disabled():
                    main_menu.enable()
                    return
            elif e.type == POLL:
                surface.fill(bg_color)
                bmessage = 'Press  and  Hold  B  to  change  sound'
                effectmessage = 'Swipe to chose effects'
                minusmessage = 'Press minus to clear effects'
                bsurface = myfont.render(bmessage, False,(0,0,0))
                brect = bsurface.get_rect(center=(x/2, y/2 -3*y/8))
                effectsurface = myfont.render(effectmessage, False, (0,0,0))
                effectrect = effectsurface.get_rect(center =(x/2, y/2 - y/4))
                minussurface = myfont.render(minusmessage, False, (0,0,0))
                mrect = minussurface.get_rect(center = (x/2, y/2 - y/8))
                list_edges()
                try:
                    old_state = wm.state
                    last_valid = (xmax/2, ymax/2)
                    run = True
                    while(run):
                        button = wm.state.get('buttons')
                        # wait_for_b_press(wm)
                        while((button == 4) or (button == 516) or (button == 260)): # while b is pressed
                            current_state = wm.state
                            # if(effect_on):
                            #    modulate_effect(current_state)
                            surface.fill(bg_color)
                            if (old_state != current_state):
                                try:
                                    xcoord = current_state['ir_src'][0]['pos'][0]
                                    ycoord = current_state['ir_src'][0]['pos'][1]
                                    last_valid = (xcoord, ycoord)
                                    position = 'x: {}, y: {}'.format(xcoord, ycoord)
                                    positionmessage = myfont.render(position, False, (0,0,0))
                                    positionrect = positionmessage.get_rect(center=(x/2,y/2))
                                    surface.blit(positionmessage,positionrect)
                                    pygame.display.update()
                                    list_edges()
                                except TypeError:
                                    # hitting this means you went out of frame somewhere
                                    # your last valid coordinates will be xcoord & ycoord
                                    surface.fill(bg_color)
                                    
                                    if(last_valid[0] < tolerance): # close to right edge
                                        rightedge = myfont.render('Tremolo',False, COLOR_GREEN)
                                        surface.blit(rightedge, (13*x/16,y/2))
                                        #GPIO.output(chan_dict['distortion'], GPIO.LOW)
                                        #GPIO.output(chan_dict['reverb'], GPIO.LOW)
                                        #GPIO.output(chan_dict['delay'], GPIO.LOW)
                                        GPIO.output(chan_dict['chorus'], GPIO.HIGH)
                                        effect_on = True
                                    
                                    elif(abs(last_valid[0]-xmax) < tolerance): # close to left edge
                                        leftedge = myfont.render('Delay',False, COLOR_GREEN)
                                        delaymessage = 'Press <- or  -> while holing B to switch lead speaker'
                                        delaysurface = myfont.render(delaymessage, False, (0,0,0))
                                        
                                        GPIO.output(chan_dict['base_delay'], GPIO.HIGH)
                                        if(button == 260): # user presses B+left
                                            GPIO.output(chan_dict['trigger_delay'], GPIO.HIGH)
                                            leftedge = myfont.render('Delay Left',False, COLOR_GREEN)
                                        elif(button == 516): # user presses B+right
                                            GPIO.output(chan_dict['trigger_delay'], GPIO.LOW)
                                            leftedge = myfont.render('Delay Right', False, COLOR_GREEN)
                                        surface.blit(delaysurface, (x/16, y/2 + y/8))
                                        surface.blit(leftedge, (x/16,y/2))
                                        #GPIO.output(chan_dict['distortion'], GPIO.LOW)
                                        #GPIO.output(chan_dict['reverb'], GPIO.LOW)
                                        #GPIO.output(chan_dict['chorus'], GPIO.LOW)
                                        effect_on = True
                                    elif(abs(last_valid[1]-ymax) < tolerance): # bottom edge
                                        bottomedge = myfont.render('Stereo  Reverb',False, COLOR_GREEN)
                                        bottomrect = bottomedge.get_rect(center=(x/2,15*y/16))
                                        surface.blit(bottomedge,bottomrect)
                                        #GPIO.output(chan_dict['delay'], GPIO.LOW)
                                        #GPIO.output(chan_dict['reverb'], GPIO.LOW)
                                        #GPIO.output(chan_dict['chorus'], GPIO.LOW)
                                        GPIO.output(chan_dict['reverb'], GPIO.HIGH)
                                        effect_on = True
                                    elif(last_valid[1] < tolerance): # top edge 
                                        topedge = myfont.render('Distortion',False, COLOR_GREEN)
                                        toprect = topedge.get_rect(center=(x/2,y/16))
                                        surface.blit(topedge,toprect)
                                        #GPIO.output(chan_dict['distortion'], GPIO.LOW)
                                        #GPIO.output(chan_dict['delay'], GPIO.LOW)
                                        #GPIO.output(chan_dict['chorus'], GPIO.LOW)
                                        GPIO.output(chan_dict['distortion'], GPIO.HIGH)
                                        effect_on = True
                                    else:
                                        # just ignore it in this case actually
                                        list_edges()
                                    pygame.display.update()
                                old_state = current_state
                            
                            button = wm.state.get('buttons')
                        
                        list_edges()
                        surface.blit(bsurface,brect)
                        surface.blit(effectsurface, effectrect)
                        surface.blit(minussurface, mrect)
                        pygame.display.update()
                        
                        if button == 128 and main_menu.is_disabled():
                           
                            GPIO.output(chan_dict['distortion'], GPIO.LOW)
                            GPIO.output(chan_dict['base_delay'], GPIO.LOW)
                            GPIO.output(chan_dict['trigger_delay'], GPIO.LOW)
                            GPIO.output(chan_dict['chorus'], GPIO.LOW)
                            GPIO.output(chan_dict['reverb'], GPIO.LOW)
                            effect_on = False
                            main_menu.enable()
                            return
                        elif button == 16: # minus button will clear effects
                            surface.fill(bg_color)
                            cleared = myfont.render('Cleared  Effects',False, (0,0,0))
                            clearrect = cleared.get_rect(center = (x/2,y/2))
                            surface.blit(cleared, clearrect)
                            pygame.display.update()
                            GPIO.output(chan_dict['distortion'], GPIO.LOW)
                            GPIO.output(chan_dict['base_delay'], GPIO.LOW)
                            GPIO.output(chan_dict['trigger_delay'], GPIO.LOW)
                            GPIO.output(chan_dict['chorus'], GPIO.LOW)
                            GPIO.output(chan_dict['reverb'], GPIO.LOW)
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
                                 font_color=COLOR_WHITE,
                                 font_size_title=30,
                                 font_title=pygameMenu.fonts.FONT_8BIT,
                                 menu_color=MENU_BACKGROUND_COLOR,
                                 menu_color_title=(0,0,255),
                                 menu_height=int(WINDOW_SIZE[1] * 0.6),
                                 menu_width=int(WINDOW_SIZE[0] * 0.6),
                                 onclose=PYGAME_MENU_DISABLE_CLOSE,
                                 option_shadow=False,
                                 joystick_enabled= True,
                                 text_color=COLOR_WHITE,
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
                            font_color=COLOR_WHITE,
                            font_size=60,
                            menu_alpha=100,
                            menu_color=MENU_BACKGROUND_COLOR,
                            menu_height=int(WINDOW_SIZE[1] * 0.6),
                            menu_width=int(WINDOW_SIZE[0] * 0.6),
                            onclose=PYGAME_MENU_DISABLE_CLOSE,
                            option_shadow=False,
                            joystick_enabled= True,
                            title='Sound  Clowns',
                            menu_color_title = (0,0,255),
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
