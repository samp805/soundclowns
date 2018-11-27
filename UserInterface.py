#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UserInterface.py

Open a Pygame window and display framerate.
Program terminates by pressing the ESCAPE-Key.
 
works with python2.7 and python3.4 

Author : Kyle Bouwens
License: GPL, see http://www.gnu.org/licenses/gpl.html
"""

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


POLL = pygame.USEREVENT

ABOUTUS = ['Matthew Bell','Kyle Bouwens','Timothy Kennedy','Sam Peters']

COLOR_BACKGROUND = (128, 32, 128)
COLOR_BLACK = (0, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)
FPS = 30.0
MENU_BACKGROUND_COLOR = (228, 55, 36)




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
startsurface = myfont.render('Press enter after pressing 1 + 2  on  Wiimote', False, (0,0,0))
surface.blit(startsurface,(x/2-x/4,y/2))
pygame.display.update()
try:
    wiimote = cwiid.Wiimote()
except(RuntimeError):
    surface.fill(COLOR_BACKGROUND)
    failsurface = myfont.render('Failed to connect ... is Bluetooth on?', False, (0,0,0))
    surface.blit(failsurface,(x/2-x/4,y/2))
    pygame.display.update()
    time.sleep(5)
    raise
successsurface = myfont.render('Connection Successful', False, (0,0,0))
surface.blit(successsurface,(x/2-x/4,y/2+y/4))
pygame.display.update()    

# print initial state
wiimote.rpt_mode = cwiid.RPT_ACC | cwiid.RPT_IR | cwiid.RPT_BTN
wiimote.led = 1
time.sleep(1) # let the sensors wake up

with open('./data/example.json', 'w+') as f:
    f.write(json.dumps(wiimote.state, sort_keys=True, indent=4))



# -----------------------------------------------------------------------------

def main_background():
    """
    Function used by menus, draw on background while menu is active.

    :return: None
    """
    surface.fill(COLOR_BACKGROUND)
# -----------------------------------------------------------------------------
def wiidata(wm):
    """
    Function used to get wiimote data and write as to json
    :param wmstate: wiimote state dictionary
    :return: None
    """

    main_menu.disable()
    main_menu.reset(1)

    bg_color = COLOR_BACKGROUND
    old_state = wm.state
    t0 = time.time()

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
                current_state = wm.state
                button = wm.state.get('buttons')
                if (button == 4):
                    pygame.display.flip()
                    if (old_state != current_state):
                        print(wm.state)
                        old_state = current_state
                        dt = time.time() - t0
                        t0 = time.time()
                        print(dt)
                    try:
                        pygame.draw.circle(surface, COLOR_GREEN, (100, 100), 50, 0)
                        xcoord = current_state['ir_src'][0]['pos'][0]
                        ycoord = current_state['ir_src'][0]['pos'][1]
                        xcoord = (xcoord/1024.0)*x
                        ycoord = (ycoord/768.0)*y
                        pygame.draw.circle(surface, COLOR_BLACK, (xcoord,ycoord),50,0)
                        
                    except:
                        pygame.draw.circle(surface, COLOR_GREEN, (100, 100), 50, 0)
                        
                        
                elif button == 128 and main_menu.is_disabled():
                    main_menu.enable()
                    return
                else:
                    pygame.display.flip()
                    pygame.event.clear(POLL)

                                    


        # Pass events to main_menu
        surface.fill(bg_color)
        pygame.draw.circle(surface, COLOR_BLACK, (100, 100), 50, 0)
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
about_us_menu.add_option('Return to menu', PYGAME_MENU_BACK)

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
                            title='Sound Clowns',
                            window_height=WINDOW_SIZE[1],
                            window_width=WINDOW_SIZE[0],
                            wiimote=wiimote
                            )

main_menu.add_option('Start', wiidata, wiimote)
main_menu.add_option('About Us', about_us_menu)
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
