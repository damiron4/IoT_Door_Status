from time import sleep
from esp32 import wake_on_ext0, WAKEUP_ANY_HIGH, WAKEUP_ALL_LOW
from machine import Pin, RTC, deepsleep
from network import WLAN, STA_IF
import urequests
import utime
from config import *

sensor = Pin(4, mode = Pin.IN)
now = utime.localtime()

def change_signal(status):
    if status == 1:
        # print("Wake up on door closure")
        wake_on_ext0(pin = sensor, level = WAKEUP_ANY_HIGH)
    else:
        # print("Wake up on door opening")
        wake_on_ext0(pin = sensor, level = WAKEUP_ALL_LOW)

def isOpen():
    # 1 - door is open and 0 - door is closed
    return 1 - sensor.value()

rtc = RTC()
prev_status = rtc.memory()

if prev_status == b'':
    curr_status = isOpen()
    rtc.memory(b'' + str(curr_status))
    change_signal(curr_status)
    deepsleep()
elif prev_status == b'0':
    prev_status = 0
elif prev_status == b'1':
    prev_status = 1

# wait pin change(sensor)
active = 0
while active < 20 and active > -20:
    if prev_status != isOpen():
        active += 1
    else:
        active -= 1
    sleep(0.05)
    
if active > 0:
    curr_status = 1 - prev_status
    change_signal(curr_status)
    rtc.memory(b'' + str(curr_status))

    station = WLAN(STA_IF)
    ssid = wifi_config['ssid']
    password = wifi_config['password']
    station.active(True)
    station.connect(ssid, password)

    while station.isconnected() == False:
        print("Trying to connect")
        station.connect(ssid, password)    
    print('Connection successful')
    
    if  curr_status == 1:
        text = "\U0001F7E9 The door OPENED\n\U0001F551 Time: %i:%i" % (now[3], now[4])
    else:
        text = "\U0001F7E5 The door CLOSED\n\U0001F551 Time: %i:%i" % (now[3], now[4])
    url = 'https://api.telegram.org/bot' + telegram_token_config['token'] + '/sendMessage'
    data = {'chat_id': telegram_chat_config['chat_id'], 'text': text, "parse_mode": "HTML"}
    try:
        response = urequests.get(url, json=data)
        response.close()
    except:
        print('Error sending message')

else:
    curr_status = isOpen()
    change_signal(curr_status)
    rtc.memory(b'' + str(curr_status))

sleep(1)
print('Going to deepsleep')
deepsleep()
