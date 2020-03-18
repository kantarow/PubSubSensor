import paho.mqtt.publish as publish

publish.single(topic="example/topic", payload="Hello!", hostname="mqtt.eclipse.org", port=1883)
