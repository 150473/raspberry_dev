import RPi.GPIO as GPIO
import ADC0834
from time import sleep

motionPin=23
buzzPin=26

GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzPin, GPIO.OUT)
GPIO.output(buzzPin, GPIO.HIGH)
GPIO.setup(motionPin, GPIO.IN)
ADC0834.setup()
sleep(2)

try:
    while True:
        motion = GPIO.inout(motionPin)
        lightVal = ADC0834.getResult(0)
        print('Light Value: ',lightVal, ' Motion: ',motion)
        sleep(.2)
        if motion == 1 and lightVal <= 140:
            GPIO.output(buzzPin, GPIO.LOW)
            print('Motion detected')
        else:
            print('All good')
            GPIO.output(buzzPin, GPIO.HIGH)
            
    
except KeyboardInterrupt:
    sleep(.25)
    GPIO.cleanup()
    print('GPIO good to go')

