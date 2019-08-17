from com import Encoder
from grbl import grbl
from time import sleep


# constrain to specific range
def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

# round to a specific increment, such as 0.25
def inc_round(v, inc):
    return round(v/inc)*inc


class Control(object):
    def __init__(self, g, enc, spm, inc, power, speed, init, size):
        self.grbl = g
        self.enc = enc
        self.spm = spm
        self.inc = inc
        self.power = power
        self.speed = speed
        self.init = init

        self._x, self._y = 0,0  # internal use "high res" values
        self.x, self.y = 0,0  # values constrained to specific increments

        self.grbl.unlock()
        self.cfg = self.grbl.get_config()
        # self.max_x, self.max_y = 130,130

        if size:
            self.max_x, self.max_y = size[0], size[1]
        else:
            self.max_x = self.cfg['$130']
            self.max_y = self.cfg['$131']

        self.grbl.send(self.init)
        self.set_speed(self.speed)
        self.set_power(self.power)


    def home(self):
        print('Homing...')
        self.x, self.y, _ = self.grbl.home()
        self._x, self._y = self.x, self.y
        print('Homing complete')

    def set_speed(self, speed):
        self.speed = speed
        self.grbl.send('F{}'.format(self.speed))

    def set_power(self, power):
        self.power = power
        self.grbl.send('S{}'.format(1000*self.power))

    def check(self):
        # store previous values
        lx, ly = self.x, self.y

        # read encoder deltas
        dx, dy = self.enc.read()

        # update and constrain internal values
        self._x += (dx / self.spm)
        self._y += (dy / self.spm)
        self._x = clamp(self._x, 0, self.max_x)
        self._y = clamp(self._y, 0, self.max_y)

        # round to configured increment
        self.x = inc_round(self._x, self.inc)
        self.y = inc_round(self._y, self.inc)

        return (self.x != lx or self.y != ly)

    def move(self):
        cmd = 'G1 X{0:.3f} Y{1:.3f}'.format(self.x, self.y)
        self.grbl.send(cmd)

MACHINE_CFG = {
    "size": None,           # X,Y dimensions in mm, None to autodetect
    "spm": 100,             # encoder steps per mm movement
    "inc": 0.01,            # constrain move values to this increment
    "power": 0.05,          # default power level (0.0 - 1.0)
    "speed": 5000,          # default movement speed,
    "init": "G90 G21 G54 M4"    # startup gcode
}

def main():
    g = grbl()
    enc = Encoder()
    con = Control(g, enc, **MACHINE_CFG)
    con.home()

    while True:
        if con.check():
            con.move()

        # print('{0:.2f},{1:.2f}'.format(con.x, con.y))

        # sleep(0.05)

if __name__ == '__main__':
    main()