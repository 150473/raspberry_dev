import RPi.GPIO as GPIO
from time import sleep

delay = 0.1
inPin = 40
outPin = 38

GPIO.setmode(GPIO.BOARD)
GPIO.setup(inPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(outPin, GPIO.OUT)

try:
	while True:
		readVal = GPIO.input(inPin)
		print(readVal)
		GPIO.output(outPin, readVal)
		sleep(delay)
except KeyboardInterrupt:	
	GPIO.cleanup()
	print('shutting down...')
