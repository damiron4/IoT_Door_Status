
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
esp32.wake_on_ext0(pin = sensor, level = esp32.WAKEUP_ANY_HIGH)


door_topic = b'door'
CLIENT_NAME = 'DOOR1'

def get_door(): 
    return sensor.value() # 1 or 0

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

while True:
    status = get_door()
#     print("I am here")
#     mqttc.publish(door_topic, "0")
#     print("I got here")
    mqttc.publish(door_topic,  b'' + str(status))
    print("Going to deepsleep")
    machine.deepsleep()
