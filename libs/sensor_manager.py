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

    @property
    def status_dict(self):
        return {key: sensor.status_dict for key, sensor in self.sensors}


if __name__ == '__main__':
    sm = SensorManager(PressureSensor(0x00), PressureSensor(0x00))
    for i in range(5):
        sleep(10)
        print(sm.status_dict)
