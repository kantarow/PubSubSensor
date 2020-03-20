from multiprocessing import Process, Manager
from time import sleep, time
from abc import ABCMeta, abstractmethod


class I2CBase(metaclass=ABCMeta):
    def __init__(self):
        self.__m = Manager()
        self._status_dict = self.__m.dict({})
        # TODO: getter/setterの設定(copyしなくてよいようにする)
        # TODO: 色々privateにしてみる
        # TODO: setupに色々書くのをやめる
        # TODO: 共通処理をここに書く

        self.setup()

        self.__p = Process(target=self.process, args=())
        self.__p.start()

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def process(self):
        pass

    @property
    def status_dict(self):
        return self._status_dict.copy()


class Thermistor(I2CBase):
    def __init__(self):
        super().__init__()

    def setup(self):
        self._status_dict["type"] = "thermistor"
        self._status_dict["model_number"] = "103JT-050"
        self._status_dict["measured_time"] = 0
        self._status_dict["temperature_celsius"] = 0

    def process(self):
        while True:
            sleep(3)
            self._status_dict["temperature_celsius"] += 1
            self._status_dict["measured_time"] = time()


class PressureSensor(I2CBase):
    def __init__(self):
        super().__init__()

    def setup(self):
        self._status_dict["type"] = "pressure_sensor"
        self._status_dict["model_number"] = "LPS251B"
        self._status_dict["measured_time"] = 0
        self._status_dict["pressure_hpa"] = 0
        self._status_dict["temperature_celsius"] = 0
        self._status_dict["altitude_meters"] = 0

    def process(self):
        while True:
            sleep(2)
            self._status_dict["measured_time"] = time()
            self._status_dict["pressure_hpa"] += 1
            self._status_dict["temperature_celsius"] += 1
            self._status_dict["altitude_meters"] += 1


if __name__ == "__main__":
    A = Thermistor()
    B = PressureSensor()
    while True:
        sleep(2)
        print(A.status_dict)
        print(B.status_dict)
