import RPi.GPIO as GPIO
import time
buzzerPin=17
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzerPin, GPIO.OUT)
buzz=GPIO.PWM(buzzerPin, 400)
buzz.start(50)
try:
    while True:
        buzz.ChangeFrequency(100)
        time.sleep(1)
        buzz.ChangeFrequency(400)
        time.sleep(1)
        
     #for siren effect
     #while True:
      #  for i in range (150, 2000):
       #      buzz.ChangeFrequency(i)
        #     time.sleep(.001)
             
        #for i in range (2000, 150, -1):
         #    buzz.ChangeFrequency(i)
          #   time.sleep(.001)
         
except KeyboardInterrupt:
    GPIO.cleanup()
    print('GPIO Good to Go')
