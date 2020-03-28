import paho.mqtt.client as mqtt
import json
# クライアントがサーバーからCONNACKを受けとった際に呼ばれるコールバック


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # on_connect()にsubscribe()を記述すると, 接続が切断されても再び購読できる
    client.subscribe("example/topic")

# クライアントがサーバーからPUBLISHを受け取った際に呼ばれるコールバック


def on_message(client, userdata, msg):
    print(type(msg.payload))
    print(msg.payload)
    # print(json.dumps(msg.payload, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': ')))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("mqtt.eclipse.org", 1883, 60)


# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

# mosquitto_pubを利用してこのサンプルコードでメッセージを受け取る
# mosquitto_pub -h mqtt.eclipse.org -p 1883 -t "example/topic" -m "hello"

client.loop_forever()
