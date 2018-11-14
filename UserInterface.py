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
# Import pygame and libraries
from pygame.locals import *
from random import randrange
import os
import pygame
import pygameMenu
from pygameMenu.locals import *

ABOUT = ['PygameMenu {0}'.format(pygameMenu.__version__),
         'Author: {0}'.format(pygameMenu.__author__),
         PYGAMEMENU_TEXT_NEWLINE,
         'Email: {0}'.format(pygameMenu.__email__)]
ABOUTUS = ['Matthew Bell','Kyle Bouwens','Timothy Kennedy','Sam  Peters']

COLOR_BACKGROUND = (128, 0, 128)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
FPS = 30.0
MENU_BACKGROUND_COLOR = (228, 55, 36)
WINDOW_SIZE = (1440,900)

pygame.init()

if(pygame.joystick.get_count() == 0):
    print('please connect a controller')
else:
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    name = joystick.get_name()
    print(name)
    axes = joystick.get_numaxes()
    buttons = joystick.get_numbuttons()
    hats = joystick.get_numhats()

    print("There is " + str(axes) + " axes")
    print("There is " + str(buttons) + " button/s")
    print("There is " + str(hats) + " hat/s")

# Create pygame screen and objects
surface = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption('SoundClowns')
clock = pygame.time.Clock()
dt = 1 / FPS

SHAPE = ['CIRCLE']

# -----------------------------------------------------------------------------
def change_shape(s):
    """
    Change shape to display

    :return:
    """
    print ('Selected Shape: {0}'.format(s))
    SHAPE[0] = s

def main_background():
    """
    Function used by menus, draw on background while menu is active.

    :return: None
    """
    surface.fill(COLOR_BACKGROUND)
# -----------------------------------------------------------------------------
def shape_fun(shape):
    """
    Function used to draw shapes with a given selector
    :param shape: Name of shape to be drawn
    :return: None
    """

    shape = shape[0]
    assert isinstance(shape, str)


    main_menu.disable()
    main_menu.reset(1)

    bg_color = (255,0,0)

    while True:

        # Clock tick
        clock.tick(30)

        # Application events
        shapeevents = pygame.event.get()
        for e in shapeevents:
            if e.type == QUIT:
                exit()
            elif e.type == KEYDOWN  :
                if e.key == K_ESCAPE and main_menu.is_disabled():
                    main_menu.enable()

                    return
            elif e.type == JOYBUTTONDOWN:
                if e.button == JOY_BUTTON_BACK and main_menu.is_disabled():
                    main_menu.enable()

                    return


        # Pass events to main_menu
        main_menu.mainloop(shapeevents)
        surface.fill(bg_color)
        if shape == 'CIRCLE':
            pygame.display.flip()
            pygame.draw.circle(surface, COLOR_BLACK, (500, 500), 100, 0)
        elif shape == 'RECTANGLE':

            pygame.display.flip()
            pygame.draw.rect(surface, COLOR_BLACK, [500,250,500,250])
        else:
            raise Exception('Unknown shape {0}'.format(shape))
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
                            window_width=WINDOW_SIZE[0]
                            )
main_menu.add_option('Draw', shape_fun, SHAPE)
main_menu.add_selector('Select shape', [('Circle', 'CIRCLE'),
                                        ('Rectangle', 'RECTANGLE')],
                       onreturn=None,
                       onchange=change_shape)
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