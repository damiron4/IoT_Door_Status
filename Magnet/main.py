
### --- same as before ---

### ---------------------- 
  
from umqtt.simple import MQTTClient
import time
import esp32
import ubinascii
import machine
import micropython
import network


sensor = machine.Pin(4, mode = machine.Pin.IN)


door_topic = b'door'
CLIENT_NAME = 'DOOR1'

def change_signal(status):
    if status == 1:
        print("Status open")
        esp32.wake_on_ext0(pin = sensor, level = esp32.WAKEUP_ANY_HIGH)
    else:
        print("Status closed")
        esp32.wake_on_ext0(pin = sensor, level = esp32.WAKEUP_ALL_LOW)

# 
# def wait_pin_change(pin):
#     # wait for pin to change value
#     # it needs to be stable for a continuous 20ms
#     cur_value = pin.value()
#     active = 0
#     while active < 20:
#         if pin.value() != cur_value:
#             active += 1
#         else:
#             active = 0
#         time.sleep(0.001)

# def connect_mqtt():
# station = network.WLAN(network.STA_IF)
# ssid = "NU"
# password = "1234512345"
# station.active(True)
# station.connect(ssid, password)
# 
# while station.isconnected() == False:
#   pass
# 
# 
# print('Connection successful')
# BROKER_ADDR = 'test.mosquitto.org'
# mqttc = MQTTClient(CLIENT_NAME, BROKER_ADDR, port = 1883, keepalive=60)
# mqttc.connect()


def get_door():
    return 1 - sensor.value()
#   print("Door is closed")
        
    
#   print("Door is open")
     # 1 is open, magnet and 0 is closed

rtc = machine.RTC()
prev_stat = rtc.memory()
if prev_stat == b'':
    prev_stat = 1-get_door()
    print(prev_stat)
    change_signal(prev_stat)
elif prev_stat == b'0':
    prev_stat = 0
elif prev_stat == b'1':
    prev_stat = 1
else:
    print("wtf")
    sleep(1000)
    
    

# wait_pin_change(sensor)
active = 0
while active < 20 and active > -20:
    if prev_stat != get_door():
        active += 1
    else:
        active -= 1
    time.sleep(0.05)
    
if active > 0:
    curr_stat = 1 - prev_stat
    change_signal(curr_stat)
    rtc.memory(b'' + str(curr_stat))
#     print("I am here")
#     mqttc.publish(door_topic, "0")
#     print("I got here")
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
else:
    change_signal(prev_stat)
    rtc.memory(b'' + str(prev_stat))
print("Going to sleep")
time.sleep(3)
print("Going to deepsleep")
machine.deepsleep()
