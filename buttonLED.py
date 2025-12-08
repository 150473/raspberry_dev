import RPi.GPIO as GPIO
from time import sleep

delay = 0.1

GPIO.setmode(GPIO.BOARD)
inPin = 40
outPin = 38
GPIO.setup(inPin, GPIO.IN)
GPIO.setup(outPin, GPIO.OUT)
try:
	while True:
		readVal = GPIO.input(inPin)
		print(readVal)
		GPIO.output(outPin, readVal)
except KeyboardInterrupt:	
	GPIO.cleanup()
	print('shutting down...')
