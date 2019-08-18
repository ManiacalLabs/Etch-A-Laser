from com import Encoder

enc = Encoder()
print("Encoder done")

while True:
    print('line')
    dx, dy = enc.read()
    if dx !=0 or dy != 0:
        print('{},{}'.format(dx, dy))