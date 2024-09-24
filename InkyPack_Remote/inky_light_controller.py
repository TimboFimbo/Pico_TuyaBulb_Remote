import WIFI_CONFIG
from network_manager import NetworkManager
import time
import uasyncio
import ujson
from urllib import urequest
from picographics import PicoGraphics, DISPLAY_INKY_PACK
from pimoroni import Button
import urequests

"""

Control Tuya smart lights via Smarts Bulbs API (see https://github.com/TimboFimbo/TuyaSmartBulbs_API)

"""

graphics = PicoGraphics(DISPLAY_INKY_PACK)
button_a = Button(12)
button_b = Button(13)
button_c = Button(14)

WIDTH, HEIGHT = graphics.get_bounds()
# change the ip address to that of the computer running the api
ENDPOINT = 'http://192.168.0.116:8000'
start_random_url = ENDPOINT + '/start_random_colour_scene_async'
start_lightning_url = ENDPOINT + '/start_lightning_scene'

printed_connection_status = False
state = 'home' # states: home, scene_screen, scene_options, colours
changed_state = True

home_screen_choices = [
    "Scene: ",
    "Colours: ",
    "Brightness: ",
    "Speed: ",
    "Start",
    "Lights Off"]

scene_screen_choices = [
    "Colours",
    "Shifting",
    "Random",
    "Lightning"]

current_home_choice = 0
current_scene_choice = 3

# ******** JSON Requests ********

# names here should match those in the API

start_lightning_json = {
  "lightning_colour": {
    "red": 255,
    "green": 255,
    "blue": 255
  },
  "lightning_percent_chance": 20,
  "lightning_length": 0.4,
  "default_brightness": 10,
  "storm_brightness_range": [
    15,
    50
  ],
  "wait_time_range": [
    0.25,
    1
  ],
  "toggles": [
    {
      "name": "White Lamp"
    },
    {
      "name": "Wood Lamp"
    },
    {
      "name": "Black Lamp"
    }
  ]
}

def clear():
    graphics.set_pen(15)
    graphics.clear()

def status_handler(mode, status, ip):
    graphics.set_update_speed(2)
    clear()
    graphics.set_pen(0)
    graphics.text("Network: {}".format(WIFI_CONFIG.SSID), 10, 10, scale=2)
    status_text = "Connecting..."
    if status is not None:
        if status:
            status_text = "Connection successful!"
        else:
            status_text = "Connection failed!"

    graphics.text(status_text, 10, 30, scale=2)
    graphics.text("IP: {}".format(ip), 10, 60, scale=2)
    graphics.update()
    
def get_choice_number(plus_or_minus: int, current_choice, screen_choices):
#     global current_home_choice
#     global home_screen_choices
    
    new_choice_num = current_choice + plus_or_minus
    
    if new_choice_num >= len(screen_choices):
        new_choice_num = 0
    if new_choice_num < 0:
        new_choice_num = len(screen_choices) -1
        
    return new_choice_num    

def get_text_position(text: str, scale: int):
    text_width = graphics.measure_text(text, scale)
    return (WIDTH - text_width)/(2)

def select_option(current_choice, current_state):
    if current_state == 'home':
        if home_screen_choices[current_choice] == "Scene: ":
            return 'scene_screen'
            

def update():
    global printed_connection_status
    global changed_state
    global state
    global home_screen_choices
    global scene_screen_choices
    global current_home_choice
    global current_scene_choice
    
    graphics.set_font("bitmap8")
    graphics.set_update_speed(1)
    
    main_text_scale = 3
    other_text_scale = 2
    number_of_choices_shown = 3
    
    choices = []
    cur_screen_choices = []
    cur_selected_choice = 0
    
    for i in range(0, number_of_choices_shown):
        if state == 'home':
            choice = home_screen_choices[get_choice_number(i-1, current_home_choice, home_screen_choices)]
            if choice == 'Scene: ':
                choices.append(home_screen_choices[get_choice_number(i-1, current_home_choice, home_screen_choices)] + scene_screen_choices[current_scene_choice])
            else:                  
                choices.append(home_screen_choices[get_choice_number(i-1, current_home_choice, home_screen_choices)])
            cur_screen_choices = home_screen_choices
            cur_selected_choice = current_home_choice
        elif state == 'scene_screen':
            choices.append(scene_screen_choices[get_choice_number(i-1, current_scene_choice, scene_screen_choices)])
            cur_screen_choices = scene_screen_choices
            cur_selected_choice = current_scene_choice
    
    if printed_connection_status == False:
            uasyncio.get_event_loop().run_until_complete(network_manager.client(WIFI_CONFIG.SSID, WIFI_CONFIG.PSK))
            printed_connection_status = True
      
    if changed_state == True:
        changed_state = False
        
        for i in range(0, number_of_choices_shown):
            if state == 'home':
                choices.append(home_screen_choices[get_choice_number(i-1, cur_selected_choice, cur_screen_choices)])
                cur_screen_choices = home_screen_choices
                cur_selected_choice = current_home_choice
            elif state == 'scene_screen':
                choices.append(scene_screen_choices[get_choice_number(i-1, cur_selected_choice, cur_screen_choices)])
                cur_screen_choices = scene_screen_choices
                cur_selected_choice = current_scene_choice

        clear()
        graphics.set_pen(0)
        graphics.text(choices[0], int(get_text_position(choices[0], other_text_scale)), 10, scale=other_text_scale)
        graphics.text(choices[1], int(get_text_position(choices[1], main_text_scale)), 50, wordwrap=WIDTH - 20, scale=main_text_scale)
        graphics.text(choices[2], int(get_text_position(choices[2], other_text_scale)), 100, scale=other_text_scale)
        graphics.update()
            
#         if state == 'Start Lightning':
#             state = 'home'
#             y = urequests.post(start_lightning_url, json = start_lightning_json, headers = {'Content-Type': 'application/json'})
#             y.close()
#             print("Lightning Started")
            
def check_for_button_presses():
    global changed_state
    global current_home_choice
    global current_scene_choice
    global home_screen_choices
    global scene_screen_choices
    global state
    
    if changed_state == False:
        if button_a.read():
            if state == 'home':
                current_home_choice = get_choice_number(-1, current_home_choice, home_screen_choices)
                #set_current_home_choices(-1)
                changed_state = True
            elif state == 'scene_screen':
                current_scene_choice = get_choice_number(-1, current_scene_choice, scene_screen_choices)
                #set_current_home_choices(-1)
                changed_state = True            
                
        if button_c.read():
            if state == 'home':
                current_home_choice = get_choice_number(1, current_home_choice, home_screen_choices)
                #set_current_home_choices(1)
                changed_state = True
            elif state == 'scene_screen':
                current_scene_choice = get_choice_number(1, current_scene_choice, scene_screen_choices)
                #set_current_home_choices(-1)
                changed_state = True   
                
        if button_b.read():
            if state == 'home':
                state = select_option(current_home_choice, state)
            elif state == 'scene_screen':
                    state = 'home'
            changed_state = True

network_manager = NetworkManager(WIFI_CONFIG.COUNTRY, status_handler=status_handler)
while True:
    update()
    check_for_button_presses()
    time.sleep(0.1)