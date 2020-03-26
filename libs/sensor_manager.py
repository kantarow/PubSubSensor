from sensor_mp import Thermistor, PressureSensor, Accelerometer, TemperatureHumiditySensor, PulseWaveSensor
from time import sleep
from multiprocessing import Lock


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
            sensor._close()

    def active_sensors(self):
        return tuple([sensor.is_active for _, sensor in self.sensors])

    @property
    def status_dict(self):
        return {key: sensor.status_dict for key, sensor in self.sensors}
    # TODO: センサーが生きているかどうかのタプルを返すメソッド


if __name__ == '__main__':
    lock = Lock()
    sensors = [
        Thermistor("1", lock),
        Thermistor("2", lock),
        PressureSensor(),
        Accelerometer("5", lock),
        TemperatureHumiditySensor(),
        PulseWaveSensor()
    ]
    with SensorManager(*sensors) as sm:
        for i in range(5):
            print(sm.status_dict)
            print(sm.active_sensors)
            sleep(1)
