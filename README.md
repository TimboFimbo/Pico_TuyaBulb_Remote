# Pico TuyaBulb Remote
For controlling a Tuya SmartLight server, using a Raspberry Pi Pico and RGB Keypad

This application will change the color and brightness of Tuya Smart Bulbs, as well as trigger multi-bulb scenes. In order to use it you will need the following:

- A copy of the Smart Light server, found at https://github.com/TimboFimbo/TuyaSmartBulbs_API (still a work in progress)
- Something to run the server on (such as a Raspberry Pi or old PC)
- Some Tuya-powered Smart Bulbs (check Amazon or local stores)
- A Raspberry Pi Pico W (with headers)
- The Pimoroni Pico MicroPython firmware (https://github.com/pimoroni/pimoroni-pico/releases)
- A Pimoroni Pico RGB Keypad (https://shop.pimoroni.com/products/pico-rgb-keypad-base?variant=32369517166675)

Once all set up and running, the keypad should light up with various colors. The top row is being worked on (see below). The other buttons can be pressed once to change all of the available smart lights in your house to the chosen color. Pressing a button multiple times cycles though brightnesses, which will be sent to the lights when you stop pressing.

Notes and TODOs:

- I've started adding the ability to trigger scenes, using the top row buttons. They start with a 60 minute wait time between changes, and pressing each button multiple times cycles through wait times - they're' currently set to 60 mins, 10 mins, 1 min, then 1 sec, but this may change. The buttons are currently set as follows:
    - 0: Switch all lights to RGB(0, 0, 0). This turns most bulbs off, but not strip lights. I'll change this to a proper power on and off soon.
    - 1: Switch all lights to white. I'm planning on replacing this.
    - 2: Trigger Random Colour Scene, with all bulbs and colours used.
    - 3: Trigger Xmas Scene, which I'll replace with the Multi-Colour Scene soon.

- Although everything works, it was started as a simple script to light up the keypad buttons, but is getting more complex over time. It's not unreadable, but it needs some tidying up before much more is added.
