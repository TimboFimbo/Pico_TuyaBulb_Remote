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
start_shifting_url = ENDPOINT + '/start_multi_colour_scene_async'
start_random_url = ENDPOINT + '/start_random_colour_scene_async'
start_lightning_url = ENDPOINT + '/start_lightning_scene'

printed_connection_status = False
state = 'home' # states: home, scene_screen, scene_options, colours, start
changed_state = True

home_screen_choices = [
    "Scene: ",
    "Colours: ",
    "Brightness: ",
    "Speed: ",
    "Bulbs: ",
    "Start",
    "Lights Off"]

scene_screen_choices = [
    "Colours",
    "Shifting",
    "Random",
    "Lightning"]

colours_screen_choices = [
    "Default",
    "Select All",
    "Red",
    "Green",
    "Blue",
    "Done"]

brightness_screen_choices = [
    "Default",
    "V. Low",
    "Low",
    "Medium",
    "High",
    "V. High"]

speed_screen_choices = [
    "Default",
    "V.Slow",
    "Slow",
    "Medium",
    "Fast",
    "V. Fast"]

bulbs_screen_choices = [
    "Default",
    "Select All",
    "Black Lamp",
    "White Lamp",
    "Wood Lamp",
    "Den Light",
    "Chair Light",
    "Sofa Light"]

current_home_choice = 0
current_scene_choice = 3
current_colours_choice = 0
current_brightness_choice = 0
current_speed_choice = 0
current_bulbs_choice = 0

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

start_shifting_json = {
  "wait_time": 600,
  "bulb_lists": [
    [
      {
        "name": "Black Lamp",
        "bright_mul": 0.5,
        "toggle": True
      },
      {
        "name": "Chair Light",
        "bright_mul": 2,
        "toggle": True
      },
      {
        "name": "Den Light",
        "bright_mul": 2,
        "toggle": True
      },
      {
        "name": "Sofa Light",
        "bright_mul": 2,
        "toggle": True
      }
    ],
    [
      {
        "name": "White Lamp",
        "bright_mul": 1,
        "toggle": True
      },
      {
        "name": "Wood Lamp",
        "bright_mul": 1,
        "toggle": True
      }
    ]
  ],
  "colour_list": [
    {
      "red": 255,
      "green": 128,
      "blue": 0
    },
    {
      "red": 255,
      "green": 0,
      "blue": 128
    },
    {
      "red": 0,
      "green": 128,
      "blue": 255
    },
    {
      "red": 128,
      "green": 255,
      "blue": 0
    },
    {
      "red": 128,
      "green": 0,
      "blue": 255
    }
  ]
}

start_random_json = {
  "wait_time": 600,
  "toggles": [
    {
      "name": "Black Lamp",
      "bright_mul": 0.5,
      "toggle": True
    },
    {
      "name": "White Lamp",
      "bright_mul": 1,
      "toggle": True
    },
    {
      "name": "Chair Light",
      "bright_mul": 2,
      "toggle": True
    },
    {
      "name": "Den Light",
      "bright_mul": 2,
      "toggle": True
    },
    {
      "name": "Wood Lamp",
      "bright_mul": 1,
      "toggle": True
    },
    {
      "name": "Sofa Light",
      "bright_mul": 2,
      "toggle": True
    }
  ],
  "colour_list": [
    {
      "red": 255,
      "green": 0,
      "blue": 0
    },
    {
      "red": 0,
      "green": 255,
      "blue": 0
    },
    {
      "red": 0,
      "green": 0,
      "blue": 255
    },
    {
      "red": 255,
      "green": 0,
      "blue": 128
    },
    {
      "red": 255,
      "green": 0,
      "blue": 255
    },
    {
      "red": 128,
      "green": 0,
      "blue": 255
    },
    {
      "red": 0,
      "green": 128,
      "blue": 255
    },
    {
      "red": 0,
      "green": 255,
      "blue": 255
    },
    {
      "red": 0,
      "green": 255,
      "blue": 128
    },
    {
      "red": 128,
      "green": 255,
      "blue": 0
    },
    {
      "red": 255,
      "green": 255,
      "blue": 0
    },
    {
      "red": 255,
      "green": 128,
      "blue": 0
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
    
def send_request(): # for now, this only sends the defaults
    global state
    global changed_state
    global scene_screen_choices
    global current_scene_choice
    
    message = "Sending Request..."
    message_scale = 2
    clear()
    graphics.set_pen(0)
    graphics.text(message, int(get_text_position(message, message_scale)), 50, scale=message_scale)
    graphics.update()

    if scene_screen_choices[current_scene_choice] == "Shifting":
        y = urequests.post(start_shifting_url, json = start_shifting_json, headers = {'Content-Type': 'application/json'})
        y.close()
        print("Shifting Scene Started")
    elif scene_screen_choices[current_scene_choice] == "Random":
        y = urequests.post(start_random_url, json = start_random_json, headers = {'Content-Type': 'application/json'})
        y.close()
        print("Random Scene Started")
    elif scene_screen_choices[current_scene_choice] == "Lightning":
        y = urequests.post(start_lightning_url, json = start_lightning_json, headers = {'Content-Type': 'application/json'})
        y.close()
        print("Lightning Scene Started") 
        
    state = 'home'
    
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
        if home_screen_choices[current_choice] == "Start":
            return 'start'    

def update():
    global printed_connection_status
    global changed_state
    global state
    global home_screen_choices
    global scene_screen_choices
    global current_home_choice
    global current_scene_choice
    
    graphics.set_font("bitmap6")
    graphics.set_update_speed(2)
    
    main_text_scale = 3
    other_text_scale = 2
    help_text_scale = 1
    number_of_choices_shown = 3
    
    choices = []
    cur_screen_choices = []
    cur_selected_choice = 0
    
    home_help = "Press A / C to Scroll. Press B to Select. Hold B to Start"
    scene_help = "Press A / C to Scroll. Press B to Select."
    
    cur_help_message = home_help
    
    for i in range(0, number_of_choices_shown):
#         if state == 'home' or state == 'start':
        if state == 'home':
            choice = home_screen_choices[get_choice_number(i-1, current_home_choice, home_screen_choices)]
            cur_help_message = home_help
            
            if choice == 'Scene: ':
                choices.append(home_screen_choices[get_choice_number(i-1, current_home_choice, home_screen_choices)] + scene_screen_choices[current_scene_choice])
            elif choice == 'Colours: ':
                choices.append(home_screen_choices[get_choice_number(i-1, current_home_choice, home_screen_choices)] + colours_screen_choices[current_colours_choice])
            elif choice == 'Brightness: ':
                choices.append(home_screen_choices[get_choice_number(i-1, current_home_choice, home_screen_choices)] + brightness_screen_choices[current_brightness_choice])
            elif choice == 'Speed: ':
                choices.append(home_screen_choices[get_choice_number(i-1, current_home_choice, home_screen_choices)] + speed_screen_choices[current_speed_choice])
            elif choice == 'Bulbs: ':
                choices.append(home_screen_choices[get_choice_number(i-1, current_home_choice, home_screen_choices)] + bulbs_screen_choices[current_bulbs_choice])
            else:                  
                choices.append(home_screen_choices[get_choice_number(i-1, current_home_choice, home_screen_choices)])
            
            cur_screen_choices = home_screen_choices
            cur_selected_choice = current_home_choice
            
        elif state == 'scene_screen':
            choices.append(scene_screen_choices[get_choice_number(i-1, current_scene_choice, scene_screen_choices)])
            cur_help_message = scene_help
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
                
#             elif state == 'start':
#                 send_request()
#                 choices.append(home_screen_choices[get_choice_number(i-1, cur_selected_choice, cur_screen_choices)])
#                 cur_screen_choices = home_screen_choices
#                 cur_selected_choice = current_home_choice

        clear()
        graphics.set_pen(0)
        graphics.text(choices[0], int(get_text_position(choices[0], other_text_scale)), 10, scale=other_text_scale)
        graphics.text(choices[1], int(get_text_position(choices[1], main_text_scale)), 40, wordwrap=WIDTH - 20, scale=main_text_scale)
        graphics.text(choices[2], int(get_text_position(choices[2], other_text_scale)), 80, scale=other_text_scale)
        graphics.text(cur_help_message, int(get_text_position(cur_help_message, help_text_scale)), 110, scale=help_text_scale)
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
    
    hold_time_to_start = 2
    
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
                start_hold = time.time()
                held_time = 0
                state = select_option(current_home_choice, state)
                while button_b.pressed:
                    held_time = time.time() - start_hold
                    print("Held time: " + str(held_time))
                    if held_time > hold_time_to_start:
                        state = 'start'
                        break
                    time.sleep(0.1)
                    button_b.read()
                print("Button released")
                
            elif state == 'scene_screen':
                    state = 'home'
            
            if state == 'start': # perform action when 'start' is selected
                send_request()
                state = 'home'
            
            changed_state = True

network_manager = NetworkManager(WIFI_CONFIG.COUNTRY, status_handler=status_handler)
while True:
    update()
    check_for_button_presses()
    time.sleep(0.1)