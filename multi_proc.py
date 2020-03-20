from multiprocessing import Process, Manager
from time import sleep
from abc import ABCMeta, abstractmethod

# TODO: 各センサの抽象基底クラスをabcで実装(__setupと__processだけ定義するようにする)
# TODO: 各センサの値は読み込み完了次第辞書として更新する
# TODO: ↑を総括して一つの辞書を返すクラスをつくる


class BaseClass(metaclass=ABCMeta):
    def __init__(self):
        self._m = Manager()
        self.status_dict = self._m.dict({})

        self.setup()

        self._p = Process(target=self.process, args=())
        self._p.start()

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def process(self):
        pass


class Aclass(BaseClass):
    def __init__(self):
        super().__init__()

    def setup(self):
        self.status_dict["type"] = "sensor_a"
        self.status_dict["model_number"] = "hogehoge"
        self.status_dict["measured_time"] = 0

    def process(self):
        while True:
            sleep(1)
            self.status_dict["measured_time"] += 1


class Bclass(BaseClass):
    def __init__(self):
        super().__init__()

    def setup(self):
        self.status_dict["type"] = "sensor_b"
        self.status_dict["model_number"] = "hugahuga"
        self.status_dict["measured_time"] = 0

    def process(self):
        while True:
            sleep(1.5)
            self.status_dict["measured_time"] += 1


if __name__ == "__main__":
    A = Aclass()
    B = Bclass()
    while True:
        sleep(2)
        print(A.status_dict.copy(), B.status_dict.copy())
