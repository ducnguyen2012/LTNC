import RPi.GPIO as GPIO 
import smbus 
import time 
from datetime import datetime
# Define GPIO to LCD mapping
LCD_RS = 5
LCD_E  = 6
LCD_D4 = 12
LCD_D5 = 13
LCD_D6 = 16
LCD_D7 = 19

# Define some device constants
LCD_WIDTH = 16    # S? lu?ng ký t? hi?n th? trên 1 hàng = MAX = 16
LCD_CHR = True	  # LCD nh?n d? li?u d?ng ký t?
LCD_CMD = False	  # Chân l?a ch?n thanh ghi d? li?u (DATA Register) ho?c thanh ghi l?nh (Instruction Register) H: Data register, L: Instruction Register --> Ghi vào chân RS
 
LCD_LINE_1 = 0x80 # Ð?a ch? LCD RAM cho dòng 1
LCD_LINE_2 = 0xC0 # Ð?a ch? LCD RAM cho dòng 2
 
# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

start_stop_pin = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
GPIO.setup(LCD_E, GPIO.OUT)  # E
GPIO.setup(LCD_RS, GPIO.OUT) # RS
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
GPIO.setup(LCD_D7, GPIO.OUT) # DB7

GPIO.setup(start_stop_pin, GPIO.IN)

DS1307 = 0x68 # DIA CHI CUA DS1307
bus = smbus.SMBus(1)
#các hàm s? d?ng trong truy?n thông I2C 
#write_byte(addr,val) g?i 1 byte d? li?u
#read_byte(addr) d?c 1 byte d? li?u
#write_i2c_block_data(addr,cmd,vals) g?i m?ng d? li?u
#read_i2c_block_data(addr,cmd)
def BCD2DEC(bcd): 
 # dec = (((bcd>>4)&0x07)*10 + bcd&0x0F)
 dec = ((bcd//16)*10 + bcd%16) 
 return dec 
def DEC2BCD(dec): 
 bcd = (dec//10)*16 + dec%10
 return bcd
 
def readDS1307(): 
 bus.write_byte(DS1307,0x00) 
 data = bus.read_i2c_block_data(DS1307,0x00,0x07) 
 #print("THis is my data in readDS1307(): "+str(data))
 #print("this is my DS1307 address: "+str(DS1307))
 second = BCD2DEC(data[0]) 
 #print("BCD2DEC(data[0]) : "+str(second))
 minute = BCD2DEC(data[1]) 
 hour = BCD2DEC(data[2]) 
 wday = BCD2DEC(data[3]) 
 day = BCD2DEC(data[4]) 
 month = BCD2DEC(data[5]) 
 year = BCD2DEC(data[6])
 year += 2000
 clock = str(hour) + ":" + str(minute) + ":" + str(second)
 ngay_hien_tai = str(day) + "/" + str(month) + "/" + str(year)
 return clock,ngay_hien_tai
 
def find_number_of_second():
 bus.write_byte(DS1307,0x00) 
 data = bus.read_i2c_block_data(DS1307,0x00,0x07) 
 second = BCD2DEC(data[0]) 
 
 return second

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command
 
  GPIO.output(LCD_RS, mode) # RS
 
  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)
 
def lcd_string(message,line):
  # Send string to display
  message = message.ljust(LCD_WIDTH," ")
  lcd_byte(line, LCD_CMD)
 
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

# Hàm d? l?y th?i gian nh?n nút
def get_button_press_time(pin):
    # Ð?i nút du?c nh?n
    start = 10000
    end = 0
    press_time = 0
    

    # Ð?i nút du?c th?
    #! tinh thoi gian ke tu khi bat dau nhan nut cho toi khi nha ra
    cnt = 0
    while GPIO.input(start_stop_pin) == 0:
      # Tính th?i gian nh?n nút
      #end_time = time.time_ns()
     if cnt == 0:
      #start = find_number_of_second()
      start = time.time_ns()/(10**9)
      cnt += 1    
    #end = find_number_of_second()
    end = time.time_ns()/(10**9)
    press_time = end-start
    #print(press_time)
    #print(press_time/(10**8))
    if int(press_time/(10**7)) != 171:
      #hienthi(str(press_time),"  ",LCD_LINE_1,LCD_LINE_2)
      return press_time
    return 0
def HenGio(mode_pin):
   if get_button_press_time(mode_pin) > 2:
      hienthi("SET ALARM","DM SON",LCD_LINE_1,LCD_LINE_2)
def BamGio():
   pass
def find_char_to_replace(old_string, replace_char_at_index, new_character, your_line):
   if your_line == LCD_LINE_1:
      lcd_byte(0x80,0)
   elif your_line == LCD_LINE_2:
      lcd_byte(0xC0,0)
   #! replace char at that index: 
   string = old_string
   index = replace_char_at_index
   new_char = new_character

   string_list = list(string)
   string_list[index] = new_char
   new_string = "".join(string_list)
   # hien thi dich chuyen con tro sang ben phai
   for i in range (replace_char_at_index):
      time.sleep(1)
      lcd_byte(0x14,0)	#D?ch chuy?n con tr? sang ph?i
   time.sleep(1)
   
   
   
   

   return new_string

def hienthi(clock,ngay_hien_tai,LCD_LINE_1,LCD_LINE_2):
   lcd_string(clock,LCD_LINE_1)
   lcd_string(ngay_hien_tai,LCD_LINE_2)
def main():
  # Initialise display
  lcd_init()
  while True:
    # Nhan du lieu
    [clock, ngay_hien_tai] = readDS1307() 

    #time = get_button_press_time(start_stop_pin)
    HenGio(start_stop_pin)
    # Hien thi
    #lcd_string(clock,LCD_LINE_1)
    
    
    #lcd_string(press_time,LCD_LINE_2)
    #lcd_string(ngay_hien_tai,LCD_LINE_2)
    #hienthi(str(press_time),ngay_hien_tai,LCD_LINE_1,LCD_LINE_2)
    
    lcd_byte(0x02, 0)	# Ð?t d?a ch? 0x00 cho DDRAM t? thanh ghi AC và dua con tr? v? v? trí g?c. N?i dung c?a thanh ghi DDRAM v?n gi? nguyên.
    lcd_byte(0x07,0)	#I/D thi?t l?p hu?ng di chuy?n c?a con tr? và S thi?t l?p s? d?ch chuy?n hi?n th?. 
    lcd_byte(0x0F,0)	#Các bít di?u khi?n Hi?n th? (D), con tr? (C) và nh?p nháy (B)
    #new_clock  = find_char_to_replace(clock, 4, 'a',LCD_LINE_1)
    #hienthi(clock,ngay_hien_tai,LCD_LINE_1,LCD_LINE_2)
    lcd_byte(0x02, 0)	# Ð?t d?a ch? 0x00 cho DDRAM t? thanh ghi AC và dua con tr? v? v? trí g?c. N?i dung c?a thanh ghi DDRAM v?n gi? nguyên.
    lcd_byte(0x07,0)	#I/D thi?t l?p hu?ng di chuy?n c?a con tr? và S thi?t l?p s? d?ch chuy?n hi?n th?. 
    lcd_byte(0x0F,0)	#Các bít di?u khi?n Hi?n th? (D), con tr? (C) và nh?p nháy (B)
    
    #lcd_byte(0x80,0)	#Ðua con tr? v? dòng 1
    #lcd_byte(0xC0,0)	#Ðua con tr? xu?ng dòng 2
    
    #for i in range (12):
      #lcd_byte(0x14,0)	#D?ch chuy?n con tr? sang ph?i
      #time.sleep(1)
    #lcd_byte(0x14,0)
    
    time.sleep(2)
    

if __name__ == '__main__':
 
  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Goodbye!",LCD_LINE_1)
    GPIO.cleanup()
