from json import dumps
from multiprocessing import Lock
from paho.mqtt import publish
from time import sleep
from libs.sensor_manager import SensorManager
from libs.sensor_mp import Thermistor, PressureSensor, Accelerometer, TemperatureHumiditySensor, PulseWaveSensor


def main():
    lock = Lock()
    sensors = [
        Thermistor("1", lock),
        Thermistor("2", lock),
        PressureSensor(),
        Accelerometer("5", lock),
        TemperatureHumiditySensor(),
        PulseWaveSensor()
    ]
    sleep(3)
    with SensorManager(*sensors) as sm:
        print("connected.")
        while all(sm.active_sensors()):
            pub_data = dumps(sm.status_dict)
            publish.single(topic="example/topic", payload=pub_data, hostname="mqtt.eclipse.org", port=1883)
            sleep(1)


if __name__ == "__main__":
    main()
