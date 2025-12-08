import RPi.GPIO as GPIO
import time

b1pin=40
b2pin=38
b1state=1
b1stateold=1
b2state=1
b2stateold=1
ledpin = 37

pwmFrequency = 1000
pwmDutyCycle = 99

GPIO.setmode(GPIO.BOARD)
GPIO.setup(b1pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(b2pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ledpin, GPIO.OUT)

myPwm=GPIO.PWM(ledpin, pwmFrequency)
myPwm.start(pwmDutyCycle)
try:
    while True:
        b1state = GPIO.input(b1pin)
        b2state = GPIO.input(b2pin)
        if b1stateold==0 and b1state==1 :
            pwmDutyCycle = pwmDutyCycle/2
            print('Dim event')
            
        if b2stateold==0 and b2state==1 :
            pwmDutyCycle = pwmDutyCycle * 2
            print('Bright event')
            
        if pwmDutyCycle > 99 :
            pwmDutyCycle = 99
        if pwmDutyCycle < 0 :
            pwmDutyCycle = 0
        
        myPwm.ChangeDutyCycle(pwmDutyCycle)
        b1stateold = b1state
        b2stateold = b2state
        time.sleep(.1)
except KeyboardInterrupt:
    myPwm.stop()
    GPIO.cleanup()
    print('GPIO good to go!!')