# Interactive Jetson BOARD-pin LED test; commands change physical GPIO outputs.
#LED TEST CODE

import Jetson.GPIO as GPIO

ldws_pin = 15
cruiseOn_pin = 7
cruiseOff_pin = 11

GPIO.cleanup()

GPIO.setmode(GPIO.BOARD)
GPIO.setup(ldws_pin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(cruiseOn_pin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(cruiseOff_pin, GPIO.OUT, initial=GPIO.LOW)

print("press any key to continue")

while True:
    tmp = input()

    if tmp == 'y':
        print("CRUISE OFF")
        GPIO.output(ldws_pin, GPIO.LOW)
        GPIO.output(cruiseOn_pin, GPIO.LOW)
        GPIO.output(cruiseOff_pin, GPIO.HIGH)

    elif tmp == 'r':
        print("LDWS ON")
        GPIO.output(ldws_pin, GPIO.HIGH)
        GPIO.output(cruiseOn_pin, GPIO.LOW)
        GPIO.output(cruiseOff_pin, GPIO.LOW)

    elif tmp == 'g':
        print("CRUISE ON")
        GPIO.output(ldws_pin, GPIO.LOW)
        GPIO.output(cruiseOn_pin, GPIO.HIGH)
        GPIO.output(cruiseOff_pin, GPIO.LOW)

    else:
        print("ALL OFF")
        GPIO.output(ldws_pin, GPIO.LOW)
        GPIO.output(cruiseOn_pin, GPIO.LOW)
        GPIO.output(cruiseOff_pin, GPIO.LOW)
