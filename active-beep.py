import RPi.GPIO as GPIO
import time
buzzerPin=17
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzerPin, GPIO.OUT)

try:
    while True:
        GPIO.output(buzzerPin, GPIO.HIGH)
        time.sleep(.1)
        GPIO.output(buzzerPin, GPIO.LOW)
        time.sleep(.1)
        
except KeyboardInterrupt:
    GPIO.cleanup()
    print('GPIO Good to Go')