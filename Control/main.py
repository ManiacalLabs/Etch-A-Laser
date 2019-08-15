from com import Serial
from time import sleep


def main():
    enc = Serial(hardwareID="16C0:0483")

    x, y = 0, 0
    while True:
        resp = enc.readline()
        resp = resp.decode().strip()
        deltas = resp.split(',')
        dx = int(deltas[0])
        dy = int(deltas[1])

        x += dx
        y += dy

        print('{},{}'.format(x, y))

        sleep(0.05)

if __name__ == '__main__':
    main()