import RPi.GPIO as GPIO
from time import sleep
pwmPin = 18
freq = 50

GPIO.setmode(GPIO.BCM)
GPIO.setup(pwmPin, GPIO.OUT)
pwm = GPIO.PWM(pwmPin, freq)
pwm.start(0)
try:
    while True:
        pwmPercent = float(input('PWM Percent: '))
        pwm.ChangeDutyCycle(pwmPercent)
        sleep(.1)
        
    
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
    print('GPIO good to go')