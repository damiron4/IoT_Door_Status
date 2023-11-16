from umqtt.simple import MQTTClient
from time import sleep
from machine import RTC, deepsleep
from network import WLAN, STA_IF
from hcsr04 import HCSR04

sensor = HCSR04(trigger_pin = 5, echo_pin = 4, echo_timeout_us = 10000)

def isOpen():
    # 1 - door is open and 0 - door is closed
    distance = sensor.distance_cm()
#     if distance > 3. or distance < 0:
#         print("Door is open")
#     else:
#         print("Door is closed")
    return 1 if distance > 3. or distance < 0  else 0

rtc = RTC()
prev_stat = rtc.memory()

if prev_stat == b'0':
    prev_stat = 0
elif prev_stat == b'1':
    prev_stat = 1

curr_stat = isOpen()
rtc.memory(b'' + str(curr_stat))

if curr_stat != prev_stat:
    station = WLAN(STA_IF)
    ssid = "NUdormitory"
    password = "1234512345"
    station.active(True)
    station.connect(ssid, password)

    while station.isconnected() == False:
      pass

    print('Connection successful')
    
    CLIENT_NAME = 'DOOR554'
    BROKER_ADDR = 'test.mosquitto.org'
    PORT        = 1883
    TOPIC       = b'door/554'

    mqttc = MQTTClient(CLIENT_NAME, BROKER_ADDR, PORT, keepalive = 60)
    mqttc.connect()
    mqttc.publish(TOPIC,  b'' + str(curr_stat))

print("Going to sleep")
sleep(1)
print("Going to deepsleep")
deepsleep(5)
