from multiprocessing import Process, Manager
from time import sleep

# TODO: 各クラスで__processを実行するように変更(白久さんのを参考に)
# TODO: 各センサの抽象基底クラスをabcで実装(__setupと__processだけ定義するようにする)
# TODO: 各センサの値は読み込み完了次第辞書として更新する
# TODO: ↑を総括して一つの辞書を返すクラスをつくる


class Aclass:
    def __init__(self):
        self._m = Manager()
        self.status_dict = self._m.dict({})

        self.setup()

        self._p = Process(target=self.process, args=())
        self._p.start()

    def setup(self):
        self.status_dict["type"] = "sensor_a"
        self.status_dict["model_number"] = "hogehoge"
        self.status_dict["measured_time"] = 0

    def process(self):
        while True:
            sleep(1)
            self.status_dict["measured_time"] += 1


class Bclass:
    def __init__(self):
        self._m = Manager()
        self.status_dict = self._m.dict({})

        self.setup()

        self._p = Process(target=self.process, args=())
        self._p.start()

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
    for i in range(10):
        sleep(3)
        print(A.status_dict.copy(), B.status_dict.copy())
