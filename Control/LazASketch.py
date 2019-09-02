import sys
import time
from time import sleep

import dothat.backlight as backlight
import dothat.lcd as lcd
import dothat.touch as nav

from control import Control, clamp
from com import Encoder
from grbl import grbl

MACHINE_CFG = {
    "size": None,           # X,Y dimensions in mm, None to autodetect
    "spm": 200,             # encoder steps per mm movement
    "inc": 0.01,            # constrain move values to this increment
    "power": 0.1,          # default power level (0.0 - 1.0)
    "speed": 5000,          # default movement speed,
    "init": "G90 G21 G54 M4"    # startup gcode
}

g = grbl()
enc = Encoder()
con = Control(g, enc, **MACHINE_CFG)

backlight.set_graph(0)
lcd.set_contrast(45)

def high_sensitivity():
    """Override default high sensitivity mode.
    With 3mm acrylic it was too sensitive.
    This provides 2x gain and 64x sensitivity.
    """

    nav._cap1166._write_byte(0x00, 0b01000000)
    nav._cap1166._write_byte(0x1f, 0b00100000)

high_sensitivity()


@nav.on(nav.CANCEL)
def handle_cancel(ch, evt):
    lcd.set_cursor_position(0, 0)
    lcd.write(pad_text('Homing...'))
    con.home()
    lcd.set_cursor_position(0, 0)
    lcd.write(pad_text('Complete!'))


@nav.on(nav.UP)
def handle_up(ch, evt):
    update_power(con.power + 0.05)


@nav.on(nav.DOWN)
def handle_down(ch, evt):
    update_power(con.power - 0.05)


@nav.on(nav.LEFT)
def handle_left(ch, evt):
    pass


@nav.on(nav.RIGHT)
def handle_right(ch, evt):
    pass


@nav.on(nav.BUTTON)
def handle_button(ch, evt):
    con.toggle_mode()
    write_mode_line()

def pad_text(txt):
    if len(txt) < 16:
        p = 16 - len(txt)
        txt += " " * p

    return txt[0:16]

def write_pos_line():
    lcd.set_cursor_position(0, 0)
    txt = 'X{0:.2f} Y{1:.2f}'.format(con.x, con.y)
    lcd.write(pad_text(txt))

def write_status_line():
    lcd.set_cursor_position(0, 1)
    txt = 'Power {}%'.format(int(con.power * 100))
    lcd.write(pad_text(txt))
    backlight.set_graph(con.power)

def write_mode_line():
    lcd.set_cursor_position(0, 2)
    txt = 'MODE: {}'.format(con.mode.name)
    lcd.write(pad_text(txt))

def update_power(power):
    con.set_power(clamp(power, 0.02, 1.0))
    write_status_line()

write_pos_line()
write_status_line()
write_mode_line()

x = 0
while 1:
    x += 0.25
    x %= 360
    backlight.sweep((360.0 - x) / 360.0)

    if con.check():
        con.move()
        write_pos_line()
        write_mode_line()