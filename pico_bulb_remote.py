# Connects to Wi-Fi
# Sends Rest API messages over network to Tuya smart light server
# Get server at https://github.com/TimboFimbo/TuyaSmartBulbs_API

import time
import picokeypad
from machine import UART, Pin
import ujson
import network
import urequests
import random

# from enum import Enum

# Set the SSID and password of your Wi-Fi network (2.4GHz only)
# Change the IP addresses of the endpoints to that of your server
ssid = 'SSID HERE'
password = 'PASSWORD HERE'
base_url = 'http://192.168.0.116:8000'
set_colour_url = 'http://192.168.0.116:8000/set_colour'
set_power_url = 'http://192.168.0.116:8000/set_power'
set_brightness_url = 'http://192.116.0.120:8000/brightness'
start_xmas_url = 'http://192.168.0.116:8000/start_xmas_scene'
start_random_url = base_url + '/start_random_colour_scene'

keypad = picokeypad.PicoKeypad()
keypad.set_brightness(1.0)

# ******** Connect to Wi-Fi network ********

CON_SLEEP_TIME = 0.25
con_colours = [[0x30, 0x00, 0xff], # colour 0
              [0x00, 0xc0, 0xc0], # colour 1
              [0xff, 0x2c, 0x2c], # colour 2
              [0x00, 0xff, 0x30], # colour 3
              [0x00, 0x00, 0x00]] # black

con_first_but = 3
con_second_but = 0
print('Waiting for connection...')
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while wlan.isconnected() == False:
    keypad.illuminate(con_first_but,
                      con_colours[4][0],
                      con_colours[4][1],
                      con_colours[4][2])
    keypad.illuminate(con_second_but,
                      con_colours[con_second_but][0],
                      con_colours[con_second_but][1],
                      con_colours[con_second_but][2])
    keypad.update()
    con_first_but = con_first_but + 1
    if con_first_but > 3:
        con_first_but = 0
    con_second_but = con_second_but + 1
    if con_second_but > 3:
        con_second_but = 0
    time.sleep(CON_SLEEP_TIME)    
ip = wlan.ifconfig()[0]
print(f'Connected on {ip}')

# ******** Variables ********

lit = 0
last_button_states = 0
colour_index = 0
power_turned_on = False
button_timer_on = False

button_press_count = 0
TIME_TO_NEXT_PRESS = 10
press_countdown = TIME_TO_NEXT_PRESS
press_counter_on = False

screenoff = False
TIME_TO_SCREENOFF = 100
screenoff_countdown = TIME_TO_SCREENOFF
just_turned_on = False

COL_BRIGHT_JUMP = 8 # check if this stuff is needed
col_multiplier = 1
cols_with_multiplier = [0, 0, 0]
current_button = 0

# for special functions and scenes
SCENE_BUTTON_TIMES = [20, 10, 4, 1] # how fast the buttons flash - try to set these automatically
SCENE_WAIT_TIMES = [3600, 600, 60, 1] # sets scene timers to 1hr | 10mins | 1min | 1sec
current_wait_time = 0
flash_countdown = SCENE_BUTTON_TIMES[current_wait_time]

XMAS_BUTTON = 3
xmas_cur_colour = 0
xmas_scene_triggered = False

RANDOM_BUTTON = 2
random_cur_colour = 4
random_scene_triggered = False

# ******** Colour Lists ********

# these values are constant
colour =[[0x00,0x00,0x00], # black
        [0x08,0x08,0x08], # dark grey
        [0x20,0x00,0x00], # special - random scene
        [0x50,0x00,0x00], # special - xmas scene
        [0x20,0x00,0x00], # red
        [0x20,0x00,0x10], # rose
        [0x20,0x00,0x20], # magenta
        [0x10,0x00,0x20], # violet
        [0x00,0x00,0x10], # blue
        [0x00,0x10,0x20], # azure
        [0x00,0x20,0x20], # cyan
        [0x00,0x20,0x10], # spring green
        [0x00,0x20,0x00], # green
        [0x10,0x20,0x00], # chartreuse
        [0x20,0x20,0x00], # yellow
        [0x20,0x10,0x00]] # orange

# these ones change as you adjust brighness
cols_with_multiplier =[
        [0x00,0x00,0x00], # black
        [0x08,0x08,0x08], # dark grey
        [0x10,0x10,0x10], # light grey
        [0x20,0x20,0x20], # white
        [0x20,0x00,0x00], # red
        [0x20,0x00,0x10], # rose
        [0x20,0x00,0x20], # magenta
        [0x10,0x00,0x20], # violet
        [0x00,0x00,0x10], # blue
        [0x00,0x10,0x20], # azure
        [0x00,0x20,0x20], # cyan
        [0x00,0x20,0x10], # spring green
        [0x00,0x20,0x00], # green
        [0x10,0x20,0x00], # chartreuse
        [0x20,0x20,0x00], # yellow
        [0x20,0x10,0x00]] # orange

# special Colours
xmas_scene_cols = [
    [0x50,0x00,0x00], # red
    [0x00,0x50,0x00] # green
    ]

# ******** JSON Requests ********

# names here should match those in the API
bulb_toggles = [
    {
      "name": "Black Lamp",
      "toggle": True
    },
    {
      "name": "White Lamp",
      "toggle": True
    },
    {
      "name": "Chair Light",
      "toggle": True
    },
    {
      "name": "Den Light",
      "toggle": True
    },
    {
      "name": "Wood Lamp",
      "toggle": True
    },
    {
      "name": "Sofa Light",
      "toggle": True
    }      
]    

set_power_json = {
    "power": True,
    "toggles": bulb_toggles   
}

set_colour_json = {
    "red": 0,
    "green": 0,
    "blue": 0,
    "toggles": bulb_toggles 
}

start_xmas_json = {
    "wait_time" : SCENE_WAIT_TIMES[0]
}

start_random_json = {
    "wait_time": SCENE_WAIT_TIMES[0] ,
    "toggles": bulb_toggles
}

# ******** Initial illumination ********

NUM_PADS = keypad.get_num_pads()
print("num pads :")
print(NUM_PADS)

for find in range (0, NUM_PADS):
    keypad.illuminate(find, colour[find][0], colour[find][1], colour[find][2])

global c # what is this for?

# ******** Check for Button Presses ********

while True:
    button_states = keypad.get_button_states()

    if last_button_states != button_states:
        last_button_states = button_states

        if button_states > 0:
            button = 0
            
            for find in range (0, NUM_PADS):
                # check if this button is pressed and no other buttons are pressed
                if button_states & 0x01 > 0:
                    print("Button Pressed is : " + str(find))
                    keypad.illuminate(button, 25, 25, 25)
                    current_button = find
                    # for special scenes
                    if find == XMAS_BUTTON: xmas_scene_triggered = True
                    if find == RANDOM_BUTTON: random_scene_triggered = True
                            
                button_states >>= 1
                button += 1
        else:
            if press_counter_on == False:
                press_counter_on = True
                button_press_count = 0
            if screenoff == False:            
                button_press_count = button_press_count + 1
                press_countdown = TIME_TO_NEXT_PRESS
            else:            
                screenoff = False
                just_turned_on = True
            screenoff_countdown = TIME_TO_SCREENOFF
            
            # after all the checks, this is where the button actions happen
            if button_press_count > 1:
                if just_turned_on == False:
                    if xmas_scene_triggered == True or random_scene_triggered == True:
                        current_wait_time = current_wait_time + 1
                        if current_wait_time >= len(SCENE_WAIT_TIMES): current_wait_time = 0
                        start_xmas_json["wait_time"] = SCENE_WAIT_TIMES[current_wait_time]
                        start_random_json["wait_time"] = SCENE_WAIT_TIMES[current_wait_time]
                    else:
                        col_multiplier = col_multiplier + 1
                        if col_multiplier > 8: col_multiplier = 1 # check why > 8

# ******** Light Buttons ********

            for find in range (0, NUM_PADS):
                
                # add loops here - this is stupid
                cols_with_multiplier[find][0] = (colour[find][0] * col_multiplier) - 1
                cols_with_multiplier[find][1] = (colour[find][1] * col_multiplier) - 1
                cols_with_multiplier[find][2] = (colour[find][2] * col_multiplier) - 1
                
                if cols_with_multiplier[find][0] < 0: # possible change to > 255
                    cols_with_multiplier[find][0] = 0
                if cols_with_multiplier[find][1] < 0:
                    cols_with_multiplier[find][1] = 0
                if cols_with_multiplier[find][2] < 0:
                    cols_with_multiplier[find][2] = 0
                if screenoff == False: # not needed
                        
                    if find == XMAS_BUTTON:
                        keypad.illuminate(find, xmas_scene_cols[xmas_cur_colour][0],
                                          xmas_scene_cols[xmas_cur_colour][1],
                                          xmas_scene_cols[xmas_cur_colour][2])
                    elif find == RANDOM_BUTTON:
                        keypad.illuminate(find, colour[random_cur_colour][0],
                                          colour[random_cur_colour][1],
                                          colour[random_cur_colour][2])
                    else:
                        keypad.illuminate(find,
                                          cols_with_multiplier[find][0],
                                          cols_with_multiplier[find][1],
                                          cols_with_multiplier[find][2])

# ******** Perform Actions After Button Release ********

    if press_counter_on == True:
        press_countdown = press_countdown - 1
        if press_countdown <= 0:
            print("number of times pressed: " + str(button_press_count))
            press_counter_on = False
            
            if just_turned_on == False:
            # now send the request to bulbs
                if power_turned_on == False:
                    power_turned_on = True
                    x = urequests.put(set_power_url, json = set_power_json, headers = {'Content-Type': 'application/json'})
                    x.close()
                        
                set_colour_json['red'] = cols_with_multiplier[current_button][0]
                set_colour_json['green'] = cols_with_multiplier[current_button][1]
                set_colour_json['blue'] = cols_with_multiplier[current_button][2]
                print("red:" + str(cols_with_multiplier[current_button][0]))
                print("green:" + str(cols_with_multiplier[current_button][1]))
                print("blue:" + str(cols_with_multiplier[current_button][2]))
                
                if xmas_scene_triggered == True:
                    y = urequests.post(start_xmas_url, json = start_xmas_json, headers = {'Content-Type': 'application/json'})
                    xmas_scene_triggered = False
                    print('xmas scene triggered')
                elif random_scene_triggered == True:
                    y = urequests.post(start_random_url, json = start_random_json, headers = {'Content-Type': 'application/json'})
                    random_scene_triggered = False
                    print('random scene triggered')
                else:
                    y = urequests.put(set_colour_url, json = set_colour_json, headers = {'Content-Type': 'application/json'})
                print(y)
                y.close()
            else:
                just_turned_on = False

            button_press_count = 0
 
# ******** Countdowns ********
 
    screenoff_countdown = screenoff_countdown - 1
    if screenoff_countdown <= 0:
        screenoff = True
        screenoff_countdown = 0
        for find in range (0, NUM_PADS):
            keypad.illuminate(find, 0, 0, 0)
    
    # for special buttons    
    flash_countdown = flash_countdown - 1
    if flash_countdown <= 0:
        xmas_cur_colour = 1 if xmas_cur_colour == 0 else 0
        random_cur_colour = random.randrange(4, len(colour))
        
        flash_countdown = SCENE_BUTTON_TIMES[current_wait_time]
        if screenoff == False:
            keypad.illuminate(XMAS_BUTTON, xmas_scene_cols[xmas_cur_colour][0],
                              xmas_scene_cols[xmas_cur_colour][1],
                              xmas_scene_cols[xmas_cur_colour][2])
            keypad.illuminate(RANDOM_BUTTON, colour[random_cur_colour][0],
                              colour[random_cur_colour][1],
                              colour[random_cur_colour][2])
            
    keypad.update()
    time.sleep(0.1)