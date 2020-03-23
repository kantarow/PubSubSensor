# TODO: センサーを統括して辞書を返すマネージャークラス
from sensor_mp import Thermistor, PressureSensor, Accelerometer, TemperatureHumiditySensor, PulseWaveSensor
from time import sleep


class SensorManager:
    """
    センサーを統括してデータをまとめて扱うするためのクラス

    Attributes
    ----------
    sensors : tuple[int, Sensor(Inherit I2CSensorBase)]
        管理しているセンサーの一覧。それぞれに番号(1-origin)が振られている
    """

    def __init__(self, *sensors):
        self.sensors = []
        for i, sensor in enumerate(sensors):
            self.sensors.append((i, sensor))

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, trace):
        for i, sensor in self.sensors:
            try:
                sensor._bus.close()
            except Exception:
                print("Exception!")

    @property
    def status_dict(self):
        return {key: sensor.status_dict for key, sensor in self.sensors}


if __name__ == '__main__':
    with SensorManager(PressureSensor(0x00), PressureSensor(0x00)) as sm:
        for i in range(5):
            print(sm.status_dict)
            sleep(1)
