
# input pins for ws_pico_13

from machine import Pin


class Buttons():
    def __init__(self):
        self.name = "wio_terminal"
        self.up = Pin("SWITCH_U", Pin.IN)       # joystick up
        self.down = Pin("SWITCH_X", Pin.IN)     # joystick down
        self.left = Pin("SWITCH_B", Pin.IN)     # joystick left
        self.right = Pin("SWITCH_Y", Pin.IN)    # joystick right
        self.center = Pin("SWITCH_Z", Pin.IN)   # joystick center

        self.button1 = Pin("BUTTON_1", Pin.IN)  # button A
        self.button2 = Pin("BUTTON_2", Pin.IN)  # button B
        self.button3 = Pin("BUTTON_3", Pin.IN)  # button X

        # for roids.py
        self.thrust = self.center
        self.hyper = self.button1
        self.fire = self.button3
