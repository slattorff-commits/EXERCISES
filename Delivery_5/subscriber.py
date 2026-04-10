"""
Exercise 4 Take-home — MQTT Subscriber (wildcard)
===================================================
Listens for all robot data published under the wildcard topic.
No ROS required — pure Python.

Run (from any machine):
  python3 subscriber.py
"""

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

BROKER = 'broker.hivemq.com'
PORT   = 1883
TOPIC  = 'robotics_class/slattorff/#'


def on_message(client, userdata, msg, properties=None):
    value = msg.payload.decode()
    print(f'Update on {msg.topic}: {value}')


client = mqtt.Client(CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect(BROKER, PORT)
client.subscribe(TOPIC)
print(f'Listening on {BROKER} → {TOPIC} ...')
client.loop_forever()
