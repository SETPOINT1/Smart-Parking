import smbus
import time


ADDRESS = 0x27


LCD_CHR = 1 
LCD_CMD = 0 

LCD_LINE_1 = 0x80 
LCD_LINE_2 = 0xC0 

LCD_BACKLIGHT  = 0x08  


ENABLE = 0x04 

class lcd:
    def __init__(self):
        
        self.lcd_device = smbus.SMBus(3)

        
        self.lcd_write(0x33, LCD_CMD)
        time.sleep(0.005) 
        self.lcd_write(0x32, LCD_CMD)
        time.sleep(0.005)
        self.lcd_write(0x06, LCD_CMD)
        time.sleep(0.005)
        self.lcd_write(0x0C, LCD_CMD)
        time.sleep(0.005)
        self.lcd_write(0x28, LCD_CMD)
        time.sleep(0.005)
        self.lcd_write(0x01, LCD_CMD) 
        time.sleep(0.005)

    def lcd_write(self, bits, mode):
        
        self.lcd_write_four_bits(mode | (bits & 0xF0) | LCD_BACKLIGHT)
        
        self.lcd_write_four_bits(mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT)

    def lcd_write_four_bits(self, data):
       
        self.lcd_device.write_byte(ADDRESS, data | ENABLE)
        time.sleep(0.0005) 

        
        self.lcd_device.write_byte(ADDRESS, data)
        time.sleep(0.0005) 

    def lcd_display_string(self, string, line):
        if line == 1:
            self.lcd_write(LCD_LINE_1, LCD_CMD)
        if line == 2:
            self.lcd_write(LCD_LINE_2, LCD_CMD)

        for char in string:
            self.lcd_write(ord(char), LCD_CHR)

    def lcd_clear(self):
        self.lcd_write(0x01, LCD_CMD)
        time.sleep(0.002) 