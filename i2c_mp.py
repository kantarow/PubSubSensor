from multiprocessing import Process, Value
from multiprocessing.sharedctypes import Synchronized
from time import sleep
from abc import ABCMeta, abstractmethod


class I2CSensorBase(metaclass=ABCMeta):
    """
    Base class of I2C Sensor.
    """

    def __init__(self):
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

        def restore(data):
            if isinstance(data, Synchronized):
                return data.value
            return data

        return {k: restore(v) for k, v in self.__dict__.items() if not k.startswith("_")}


class Thermistor(I2CSensorBase):

    def __init__(self):
        self.type = "thermistor"
        self.model_number = "103JT-050"
        self.measured_time = Value("i", 0)
        self.temperature_celsius = Value("i", 0)
        super().__init__()

    def setup(self):
        pass

    def process(self):
        while True:
            sleep(2)
            self.measured_time.value += 1
            self.temperature_celsius.value += 1


# TODO: 圧力センサークラス
# TODO: 加速度センサークラス
# TODO: 温湿度センサークラス
# TODO: 脈波センサークラス

if __name__ == "__main__":
    Th1 = Thermistor()
    Th2 = Thermistor()
    while True:
        sleep(2)
        print(Th1.status_dict, Th2.status_dict)
