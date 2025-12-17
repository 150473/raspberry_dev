import pigpio
import time


class Servo:
    def __init__(self, servo_pin, min_pulse_width=500, max_pulse_width=2500, min_angle=0, max_angle=180):
        self.servo_pin = servo_pin
        self.min_pulse_width = min_pulse_width
        self.max_pulse_width = max_pulse_width
        self.min_angle = min_angle
        self.max_angle = max_angle
        
        self.pi=pigpio.pi()
        if not self.pi.connected:
            print("Cannot connect to pigpio daemon")
            # run command sudo pigpiod after installing it
            exit()
    

    def set_angle(self, angle):
        if angle < self.min_angle: angle = self.min_angle
        if angle > self.max_angle: angle = self.max_angle
        
        pulse_width = self.min_pulse_width + (angle / self.max_angle) * (self.max_pulse_width - self.min_pulse_width)
        self.pi.set_servo_pulsewidth(self.servo_pin, pulse_width)
    

    def stop(self):
        self.pi.set_servo_pulsewidth(self.servo_pin, GPIO.LOW)
        self.pi.stop()







SERVO_PIN = 18 
DELAY= 0.01
mainservo = Servo(SERVO_PIN,500,2500,0,180)
    
try:
    while True:
        for angle in range(0, 180+1):
            print("Moving servo to ", angle)
            mainservo.set_angle(angle)
            time.sleep(DELAY)
        
        for angle in range(180, 0-1, -1):
            print("Moving servo to ", angle)
            mainservo.set_angle(angle)
            time.sleep(DELAY)
        
        
    '''print("Moving to (0)")
    set_angle(0)
    time.sleep(2)
    
    print("Moving to (180)")
    set_angle(180)
    time.sleep(2)'''
except KeyboardInterrupt:
    print("Stopping Servo...")

finally:
    print("Stopping servo...")
    mainservo.stop()