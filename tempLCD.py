from machine import Pin, I2C, PWM
from utime import sleep
import ssd1306
I2C_SCL = Pin(17)
I2C_SDA = Pin(27)
def oled_init(test=True):
    i2c = None
    oled = None
    try:
        i2c = machine.I2C(0, scl=I2C_SCL, sda=I2C_SDA, freq=400000)
        oled_width = 128
        oled_height = 64
        oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
    except Exception as e:
        print('Exception in detecting OLED - ',e)

    if test:
        return i2c
    else:
        return oled

def oled_test():
    i2c = oled_init(test=True)
    if i2c:
        print('I2C scan -- ',i2c.scan())
    else:
        print('OLED not detected')

def oled_print(oled,text):
    oled.text(text,10,10)
    oled.show()

def oled_clear(oled):
    oled.fill(0)
    oled.show()


oled = oled_init(test=False)
oled_print(oled,"Hello World!!")
