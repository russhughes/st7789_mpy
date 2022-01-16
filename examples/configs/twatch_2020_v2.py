"""TTGO TWATCH-2020 V2 with ST7789 240x240 display"""

from machine import Pin, SPI
import axp202c
import st7789

TFA = 0
BFA = 80

def config(rotation=0, buffer_size=0, options=0):
    axp = axp202c.PMU()
    axp.enablePower(axp202c.AXP202_LDO2)
    return st7789.ST7789(
        SPI(1, baudrate=32000000, sck=Pin(18, Pin.OUT), mosi=Pin(19, Pin.OUT)),
        240,
        240,
        cs=Pin(5, Pin.OUT),
        dc=Pin(27, Pin.OUT),
        backlight=Pin(12, Pin.OUT),
        rotation=rotation,
        options=options,
        buffer_size=buffer_size)
