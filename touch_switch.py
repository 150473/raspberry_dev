#working with RFID reader like MFRC522
import time
import  RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
touchPin=17
GPIO.setup(touchPin, GPIO.IN)

try:
    while True:
        senState=GPIO.input(touchPin)
        print(senState)
        time.sleep(.1)

except:
    GPIO.cleanup()
    print('GPIO Good to Go')
