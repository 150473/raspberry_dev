import RPi.GPIO as GPIO
import time

ECHO_PIN=16
TRIG_PIN=18

'''GPIO.setmode(GPIO.BOARD)
GPIO.setup(ECHO_PIN, GPIO.IN)
GPIO.setup(TRIG_PIN, GPIO.OUT)
'''

ALERT_DIST= 15 # in cms


class UltraSonicSensor():
    def __init__(self, echopin, trigpin):
        self.echopin = echopin
        self.trigpin = trigpin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.echopin, GPIO.IN)
        GPIO.setup(self.trigpin, GPIO.OUT)




    def get_distance(self):
        GPIO.output(self.trigpin, GPIO.LOW)
        time.sleep(2E-6)
        GPIO.output(self.trigpin, GPIO.HIGH)
        time.sleep(10E-6)
        GPIO.output(self.trigpin, GPIO.LOW)
        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
        while GPIO.input(self.echopin) == GPIO.LOW:
            pass
        
        starttime = time.perf_counter()
        while GPIO.input(self.echopin) == GPIO.HIGH:
            pass
        stoptime = time.perf_counter()
        duration = stoptime - starttime
        distance = duration * 34300 / 2 
        dist = round(distance, 1)
        
        return dist
    
try:
    sensor = UltraSonicSensor(ECHO_PIN, TRIG_PIN)
    while True:
        dist = sensor.get_distance()
        print("dist is...",dist)
        if dist is None:
            print("out of range")
        else:
            print("Distance: {:.2f} cms ".format(dist))
        
        
        if dist < ALERT_DIST:
            print("Alien object detected...")
        
        time.sleep(1)
        
        
except KeyboardInterrupt:
    GPIO.cleanup()
    print("Cleanning up...")
