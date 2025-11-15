import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11,GPIO.OUT)
while True:
    try:
        GPIO.output(11,True)
        time.sleep(1)
        GPIO.output(11, False)
    except KeyboardInterrupt:
        GPIO.cleanup()
        break
