# Connects to Wi-Fi
# Sends Rest API messages over network
# to Tuya smart light server
# Adding degrees to white to first four buttons

import time
import picokeypad
from machine import UART, Pin
import ujson
import network
import urequests
# from enum import Enum

# Set the SSID and password of your Wi-Fi network (2.4GHz only)
# Change the IP addresses of the endpoints to that of your server
ssid = 'SSID HERE'
password = 'PASSWORD HERE'
set_color_url = 'http://192.168.0.119:8000/test_set_color'
set_power_url = 'http://192.168.0.119:8000/test_set_power'
set_brightness_url = 'http://192.168.0.119:8000/set_brightness'

keypad = picokeypad.PicoKeypad()
keypad.set_brightness(1.0)

# Connects to Wi-Fi network (update to loop and remove hard-coded colors)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
while wlan.isconnected() == False:
    print('Waiting for connection...')
    keypad.illuminate(3, 0x00, 0x00, 0x00)
    keypad.illuminate(0, 0x30, 0x00, 0xff)
    keypad.update()
    time.sleep(0.25)
    keypad.illuminate(0, 0x00, 0x00, 0x00)
    keypad.illuminate(1, 0x00, 0xc0, 0xc0)
    keypad.update()
    time.sleep(0.25)
    keypad.illuminate(1, 0x00, 0x00, 0x00)
    keypad.illuminate(2, 0xff, 0x2c, 0x2c)
    keypad.update()
    time.sleep(0.25)
    keypad.illuminate(2, 0x00, 0x00, 0x00)
    keypad.illuminate(3, 0x00, 0xff, 0x30)
    keypad.update()
    time.sleep(0.25)
ip = wlan.ifconfig()[0]
print(f'Connected on {ip}')

lit = 0
last_button_states = 0
colour_index = 0
power_turned_on = False
button_timer_on = False

# current_colors = [0, 0, 0]
button_press_count = 0
TIME_TO_NEXT_PRESS = 10
press_countdown = TIME_TO_NEXT_PRESS
press_counter_on = False

screenoff = False
TIME_TO_SCREENOFF = 50
screenoff_countdown = TIME_TO_SCREENOFF

COL_BRIGHT_JUMP = 8
col_multiplier = 1
cols_with_multiplier = [0, 0, 0]
current_button = 0

# set_white(10, 0) = set_colour(128, 96, 16)

color =[[0x00,0x00,0x00], # black
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

set_color_json = {
    'den_light': True,            
    'white_lamp': True,
    'wood_lamp': True,
    'black_lamp': True,
    'red': 0,
    'green': 0,
    'blue': 255,
    'no_wait': False}

set_power_json = {
  'den_light': True,
  'white_lamp': True,
  'wood_lamp': True,
  'black_lamp': True,
  'power': True,
  'no_wait': False
}

set_brightness_json = {
  'den_light': True,
  'white_lamp': True,
  'wood_lamp': True,
  'black_lamp': False,
  'brightness': 50,
  'no_wait': True
}

NUM_PADS = keypad.get_num_pads()
print("num pads :")
print(NUM_PADS)

for find in range (0, NUM_PADS):
    keypad.illuminate(find, color[find][0], color[find][1], color[find][2])
            
global c

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
#                     current_colors[0] = color[find][0]
#                     current_colors[1] = color[find][1]
#                     current_colors[2] = color[find][2]
                    current_button = find
                            
                button_states >>= 1
                button += 1
        else:
            if press_counter_on == False:
                press_counter_on = True
                button_press_count = 0
            if screenoff == False:            
                button_press_count = button_press_count + 1
                press_countdown = TIME_TO_NEXT_PRESS
            screenoff = False            
            screenoff_countdown = TIME_TO_SCREENOFF
            if button_press_count > 1:
#                 current_brightness = button_press_count
                col_multiplier = col_multiplier + 1
                if col_multiplier >= 8: # change this to > 8
                    col_multiplier = 1
            
            for find in range (0, NUM_PADS):
                
                cols_with_multiplier[find][0] = (color[find][0] * col_multiplier) - 1
                cols_with_multiplier[find][1] = (color[find][1] * col_multiplier) - 1
                cols_with_multiplier[find][2] = (color[find][2] * col_multiplier) - 1
                
                if cols_with_multiplier[find][0] < 0: # possible change to > 255
                    cols_with_multiplier[find][0] = 0
                if cols_with_multiplier[find][1] < 0:
                    cols_with_multiplier[find][1] = 0
                if cols_with_multiplier[find][2] < 0:
                    cols_with_multiplier[find][2] = 0
                if screenoff == False:                
                    keypad.illuminate(find, cols_with_multiplier[find][0], cols_with_multiplier[find][1], cols_with_multiplier[find][2])
                    
    if press_counter_on == True:
        press_countdown = press_countdown - 1
        if press_countdown <= 0:
            print("number of times pressed: " + str(button_press_count))
            press_counter_on = False
            
            # now send the request to bulbs
            if power_turned_on == False:
                power_turned_on = True
                x = urequests.put(set_power_url, json = set_power_json, headers = {'Content-Type': 'application/json'})
                x.close()
                    
            set_color_json['red'] = cols_with_multiplier[current_button][0]
            set_color_json['green'] = cols_with_multiplier[current_button][1]
            set_color_json['blue'] = cols_with_multiplier[current_button][2]
            print("red:" + str(cols_with_multiplier[current_button][0]))
            print("green:" + str(cols_with_multiplier[current_button][1]))
            print("blue:" + str(cols_with_multiplier[current_button][2]))
            y = urequests.put(set_color_url, json = set_color_json, headers = {'Content-Type': 'application/json'})
            print(y)
            y.close()
            
#             set_brightness_json['brightness'] = (button_press_count - 1) * BRIGHTNESS_JUMP
#             z = urequests.put(set_brightness_url, json = set_brightness_json, headers = {'Content-Type': 'application/json'})
#             z.close()
            button_press_count = 0
    
    screenoff_countdown = screenoff_countdown - 1
    if screenoff_countdown <= 0:
        screenoff = True
        screenoff_countdown = 0
        for find in range (0, NUM_PADS):
            keypad.illuminate(find, 0, 0, 0)
    keypad.update()
    time.sleep(0.1)