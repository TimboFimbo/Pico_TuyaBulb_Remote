# Pico TuyaBulb Remote
For controlling a Tuya SmartLight server, using a Raspberry Pi Pico and RGB Keypad

This application will change the color and brightness of Tuya Smart Bulbs. In order to use it you will need the following:

- A copy of the Smart Light server, found at https://github.com/TimboFimbo/TuyaSmartBulbs_API (still a work in progress)
- Something to run the server on (such as a Raspberry Pi or old PC)
- Some Tuya-powered Smart Bulbs (check Amazon or local stores)
- A Raspberry Pi Pico W (with headers)
- The Pimoroni Pico MicroPython firmware (https://github.com/pimoroni/pimoroni-pico/releases)
- A Pimoroni Pico RGB Keypad (https://shop.pimoroni.com/products/pico-rgb-keypad-base?variant=32369517166675)

Once all set up and running, the keypad should light up with various colors. Ignore the top row for now (see below), except for the first button, which switches the lights off. The colored buttons can be pressed once to change all of the available smart lights in your house to the chosen color. Pressing a button multiple times cycles though brightnesses, which will be sent to the lights when you stop pressing.

Notes and TODOs:

- I've started adding the ability to trigger scenes, using the top row buttons. For example, button 3 starts the Xmas Scene, with a 10 minute wait between colours changes. I'm going to add the ability to start the scenes with different timings, using multiple button presses.

- Although everything works, it was started as a simple script to light up the keypad buttons, but is getting more complex over time. It's not unreadable, but it needs some tidying up before much more is added.
