from time import sleep
from esp32 import wake_on_ext0, WAKEUP_ANY_HIGH, WAKEUP_ALL_LOW
from machine import Pin, RTC, deepsleep
from network import WLAN, STA_IF
import requests
from datetime import datetime

sensor = Pin(4, mode = Pin.IN)

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
    ssid = "NU"
    password = "1234512345"
    station.active(True)
    station.connect(ssid, password)

    while station.isconnected() == False:
      pass

    print('Connection successful')
    TELEGRAM_TOKEN = '6780969852:AAFVgqyfmj8v4bw911R-AYem5-sRD0rcekI'
    CHAT_ID = '-1002064110322'
    now = datetime.now()
    if  curr_status == 1:
        text = f"\U0001F7E9 The door <b>OPENED</b>\n\U0001F551 Time: {now.strftime('%H:%M:%S')}"
    else:
        text = f"\U0001F7E5 The door <b>CLOSED</b>\n\U0001F551 Time: {now.strftime('%H:%M:%S')}"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode":"HTML"}
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data=data)

else:
#     print("Active < 0")
    curr_status = isOpen()
    change_signal(curr_status)
    rtc.memory(b'' + str(curr_status))

sleep(1)
print("Going to deepsleep")
deepsleep()
