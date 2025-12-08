import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
rows = [11,13,15,29] #GPIO pin for rows of keypad
cols = [31,33,35,37] #GPIO pin for columns of keypad
keyPad = [[1,2,3,'A'],
          [4,5,6,'B'],
          [7,8,9,'C'],
          ['*',0,'#','D']]
noPress = True
noPressOld=True

for i in range(0,5):
    GPIO.setup(rows[i], GPIO.OUT)
    GPIO.setup(cols[i], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)



try:
    while True:
        noPress = True
        for myrow in range(0, 5):
            for mycol in range(0,5):
                GPIO.output(rows[myrow], GPIO.HIGH)
                butval = GPIO.input(cols[mycol])
                GPIO.output(rows[myrow],GPIO.LOW)
                if butval ==1:
                    butlabel = keyPad[myrow][mycol]
                    noPress = False
                
                if butval == 1 and noPress=False and noPressOld=True:
                    print('button value: ', butval)
                    print('button label: ', butlabel)
        noPressOld=noPress
        sleep(0.2)
except KeyboardInterrupt:
    sleep(0.1)
    GPIO.cleanup()
    print('GPIO Good to Go')


