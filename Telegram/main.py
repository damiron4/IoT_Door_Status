import logging
from mqtt_client import MqttClient
from telegram.ext import Application

# MQTT Settings
MQTT_BROKER = 'test.mosquitto.org'
MQTT_PORT = 1883
MQTT_TOPIC = 'door/status'

# Telegram Bot Settings
TELEGRAM_TOKEN = '6780969852:AAFVgqyfmj8v4bw911R-AYem5-sRD0rcekI'
CHAT_ID = 'DoorManagement'

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize Telegram Bot
application = Application.builder().token(TELEGRAM_TOKEN).build()

def send_telegram_message(text):
    updater.bot.send_message(chat_id=CHAT_ID, text=text)

def on_mqtt_message(client, userdata, message):
    status = message.payload.decode()
    if status in ['door closed', 'door open']:
        send_telegram_message(status)

mqtt_client = MqttClient(MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, on_mqtt_message)

def main():
    mqtt_client.start()
    application.run_polling()

if __name__ == '__main__':
    main()
