#working with RFID reader like MFRC522
import time
from mfrc522 import SimpleMFRC522
import  RPi.GPIO as GPIO

reader=SimpleMFRC522()

try:
    while True:
        cmd = input('Do you want to Read or Write ? (R / W)')
        if cmd =='W':
            txt = input('Input Your Text')
            print('Place Card on Reader')
            reader.write(txt)
        if cmd=='R':
            print('Place Card on Reader')
            id, text = reader.read()
            print('ID: ',id)
            print('Text: ',text)
            time.sleep(1)

except:
    GPIO.cleanup()
    print('GPIO Good to Go')