import paho.mqtt.client as mqtt
import asyncio
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from bar_chart import get_daily_status
import csv

load_dotenv()

# Telegram bot details
TELEGRAM_TOKEN  = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID         = os.environ.get('CHAT_ID')

# MQTT Connection details
MQTT_BROKER = os.environ.get('MQTT_BROKER')
MQTT_PORT   = int(os.environ.get('MQTT_PORT'))
MQTT_TOPIC  = os.environ.get('MQTT_TOPIC')
# MQTT_USERNAME  = os.environ.get('MQTT_USERNAME')
# MQTT_PASSWORD  = os.environ.get('MQTT_PASSWORD')

DATA_FILE = './Telegram/data.csv'

class DoorStatues:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.read_csv()
        self.daily_list = self.process_data()

    def read_csv(self):
        data = []
        try:
            with open(self.file_path, 'r') as file:
                csvReader = csv.reader(file)
                for row in csvReader:
                    data.append([datetime.strptime(row[0],'%Y-%m-%d %H:%M:%S.%f'), int(row[1])])
                return data
        except FileNotFoundError:
            print("File not found.")
            return None
        
    def filter_last_24_hours(self, data):
        filtered_data = []
        current_time = datetime.now()
        for timestamp, status in reversed(data):
            filtered_data.append([timestamp, status])
            if current_time - timestamp > timedelta(days=1):
                break
        return filtered_data

    def process_data(self):
        filtered_data = self.filter_last_24_hours(self.data)[::-1]
        return filtered_data

    def add_field(self, timestamp, status):
        with open(self.file_path, 'a', newline='') as csvfile:
            csvWriter = csv.writer(csvfile)
            csvWriter.writerow([timestamp, status])
        self.daily_list.append((timestamp, status))
        return

    def get_last_24_hours(self):
        return self.daily_list

def decoder(dct):
    if 'Timestamp' and 'Status' in dct:
        return datetime.strptime(dct['Timestamp'],'%Y-%m-%d %H:%M:%S.%f'), int(dct['Status'])
    return dct

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    asyncio.run(send_message(client,userdata,msg))

async def send_message(client, userdata, msg):
    message = int(msg.payload)
    now = datetime.now()
    door_data.add_field(now, message)
    if message == 1:
        text = f"\U0001F7E9 The door <b>OPENED</b>\n\U0001F551 Time: {now.strftime('%H:%M:%S')}"
    else:
        text = f"\U0001F7E5 The door <b>CLOSED</b>\n\U0001F551 Time: {now.strftime('%H:%M:%S')}"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode":"HTML"}
    res = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data=data)
    code = res.status_code
    if code == 200:
        print("Message send successfully")
    else:
        print(f"Message not delivered, response code {code}")

def run_mqtt():
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = lambda client, userdata, message: on_message(client, userdata, message)
    # mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()

def run_telegram_bot():
    run_mqtt()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(periodic_post(door_data))
    loop.run_forever()
    
async def post_chart(door_data):
    chart_data = door_data.get_last_24_hours()
    if chart_data is None:
        print("No data")
        return
    lastOpen = "more than a day ago"
    lastClose = "more than a day ago"  
    for timestamp, status in chart_data:
        if status == 1:
            lastOpen = timestamp
        else:
            lastClose = timestamp
    if lastOpen is not None:
        lastOpen = lastOpen.strftime("%H:%M")
    if lastClose is not None:
        lastClose = lastClose.strftime("%H:%M")

    image_path = get_daily_status(chart_data)
    text = f"Door Status for the last 24 hours\n<i>\U0001F7E9 Last Opened: {lastOpen}\n\U0001F7E5 Last Closed: {lastClose}</i>"
    data = {"chat_id": CHAT_ID, "caption": text, "parse_mode":"HTML"}
    with open(image_path, "rb") as image_file:
        res = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto", data=data, files={"photo": image_file})
    code = res.status_code
    if code == 200:
        print("Chart send successfully")
    else:
        print(f"Chart not delivered, response code {code}")

async def wait_periodically(door_data):
    while True:
        await asyncio.sleep(3600*6)
        await post_chart(door_data)

async def periodic_post(door_data):
    await wait_periodically(door_data)

if __name__ == '__main__':
    door_data = DoorStatues(DATA_FILE)
    run_telegram_bot()
