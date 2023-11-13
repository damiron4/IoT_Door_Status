from umqtt.simple import MQTTClient
import time
import esp32
import ubinascii
import machine
import micropython
import network
from hcsr04 import HCSR04

sensor = HCSR04(trigger_pin=5, echo_pin=4, echo_timeout_us=10000)

door_topic = b'door'
CLIENT_NAME = 'DOOR1'

def isOpen():
    # 1 is open, magnet and 0 is closed
    distance = sensor.distance_cm()
    if distance > 3.:
        print("door is open")
    else:
        print("door is closed")
    return 1 if distance > 3. else 0

rtc = machine.RTC()
prev_stat = rtc.memory()

# if prev_stat == b'':
#     prev_stat = 1 - isOpen()
# el
if prev_stat == b'0':
    prev_stat = 0
elif prev_stat == b'1':
    prev_stat = 1
else:
    print("wtf")
    sleep(1000)

curr_stat = isOpen()
rtc.memory(b'' + str(curr_stat))

if curr_stat != prev_stat:
    station = network.WLAN(network.STA_IF)
    ssid = "NU"
    password = "1234512345"
    station.active(True)
    station.connect(ssid, password)

    while station.isconnected() == False:
      pass

    print('Connection successful')
    BROKER_ADDR = 'test.mosquitto.org'
    mqttc = MQTTClient(CLIENT_NAME, BROKER_ADDR, port = 1883, keepalive=60)
    mqttc.connect()
    mqttc.publish(door_topic,  b'' + str(curr_stat))

print("Going to sleep")
time.sleep(3)
print("Going to deepsleep")
machine.deepsleep(5)
