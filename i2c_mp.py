from multiprocessing import Process, Value
from multiprocessing.sharedctypes import Synchronized
from time import sleep, time
from abc import ABCMeta, abstractmethod


# TODO: 例外処理
class I2CSensorBase(metaclass=ABCMeta):
    """
    I2Cセンサーを表す基底クラス
    """
    @abstractmethod
    def __init__(self, bus, address):
        self._bus = bus
        self._address = address
        self.setup()
        self._p = Process(target=self.process, args=())
        self._p.start()

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def process(self):
        # TODO: Lockを使うようにする
        pass

    @property
    def status_dict(self):

        def restore(data):
            if isinstance(data, Synchronized):
                return data.value
            return data

        return {k: restore(v) for k, v in self.__dict__.items() if not k.startswith("_")}


class Thermistor(I2CSensorBase):
    def __init__(self, bus, address):
        self.type = "thermistor"
        self.model_number = "103JT-050"
        self.measured_time = Value("d", 0.0)
        self.temperature_celsius = Value("d", 0.0)
        super().__init__(bus, address)

    def setup(self):
        pass

    def process(self):
        while True:
            sleep(4)
            self.measured_time.value = time()
            self.temperature_celsius.value += 1


class PressureSensor(I2CSensorBase):
    def __init__(self, bus, address):
        self.type = "pressure_sensor"
        self.model_number = "LPS251B"
        self.measured_time = Value("d", 0.0)
        self.pressure_hpa = Value("d", 0.0)
        self.temperature_celsius = Value("d", 0.0)
        self.altitude_meters = Value("d", 0.0)
        super().__init__(bus, address)

    def setup(self):
        pass

    def process(self):
        while True:
            sleep(2.5)
            self.measured_time.value = time()
            self.pressure_hpa.value += 0.1
            self.temperature_celsius.value += 0.1
            self.altitude_meters.value += 0.1

# TODO: 加速度センサークラス
# TODO: 温湿度センサークラス
# TODO: 脈波センサークラス


if __name__ == "__main__":
    Th1 = Thermistor("bus", 0x40)
    Th2 = Thermistor("bus", 0x60)
    Pr = PressureSensor("bus", 0x80)
    while True:
        sleep(1)
        print(Th1.status_dict, Th2.status_dict, Pr.status_dict)
