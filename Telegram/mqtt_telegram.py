import asyncio
from telegram.ext import Application
import paho.mqtt.client as mqtt
from threading import Thread

#for telegram
TELEGRAM_TOKEN = '6780969852:AAFVgqyfmj8v4bw911R-AYem5-sRD0rcekI'
CHAT_ID = '-1002064110322'

#for mqtt
MQTT_BROKER = 'test.mosquitto.org'
MQTT_PORT = 1883
MQTT_TOPIC = 'door/status'

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(MQTT_TOPIC)

def on_mqtt_message(client, userdata, msg, bot):
    asyncio.run(send_message(client,userdata,msg,bot))

async def send_message(client, userdata,msg,bot):
    message = int(msg.payload)
    print("The message is ")
    print(message)
    if message == 1:
        text = '🚪Door is open🟩'
    else:
        text = '🚪Door is closed🟥'
    await bot.send_message(chat_id=CHAT_ID, text=text)
    #, asyncio.get_event_loop()
    print("Test message sent.")

def run_mqtt():
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_mqtt_message
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_forever()

# async def send_message(bot):
#     try:
#         await bot.send_message(chat_id=CHAT_ID, text="🚪Door is open🟩 - testing works without error")
#         print("Test message sent.")
#     except Exception as e:
#         print(f"Error sending test message: {e}")

# def start_async_tasks(bot):
#     asyncio.run(send_message(bot))

def run_mqtt(bot):
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    print("Connected on_connect")
    mqtt_client.on_message = lambda client, userdata, message: on_mqtt_message(client, userdata, message, bot)
    print("Connected message")
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60) 
    print("Connected ")
    mqtt_client.loop_forever() #idk

# def start_bot(bot):
#     bot.run_polling()

def run_telegram_bot():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    bot = application.bot
    mqtt_thread = Thread(target=run_mqtt, args=(bot,))
    mqtt_thread.start()

    mqtt_thread.join()
    application.run_polling()

if __name__ == '__main__':
    run_telegram_bot()