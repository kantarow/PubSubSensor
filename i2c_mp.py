# TODO: センサーを統括して辞書を返すクラス
from multiprocessing import Process, Value
from multiprocessing.sharedctypes import Synchronized
from time import sleep, time
from abc import ABCMeta, abstractmethod


# TODO: 例外処理
class I2CSensorBase(metaclass=ABCMeta):
    """
    I2Cセンサーを表す抽象基底クラス

    Attributes
    ----------
    _bus : smbus2.SMBus
        i2cのバス
    _address : int
        そのセンサーのi2cアドレス
    _p : multiprocessing.Process
        センサーの値を取得してメンバを更新していく並列プロセス
    """

    @abstractmethod
    def __init__(self, bus, address):
        """
        センサ情報を登録してから、セットアップとデータ更新プロセスを開始する

        Parameters
        ----------
        _bus : smbus2.SMBus
            i2cのバス
        _address : int
            そのセンサーのi2cアドレス
        _p : multiprocessing.Process
            センサーの値を取得してメンバを更新していく並列プロセス
        """
        self._bus = bus
        self._address = address
        self.setup()
        self._p = Process(target=self.process, args=())
        self._p.start()

    @abstractmethod
    def setup(self):
        """
        接続前のモード設定などをする
        """
        pass

    @abstractmethod
    def process(self):
        """
        センサーの値を取得してメンバを更新するプロセス
        """
        # TODO: Lockを使うようにする
        pass

    @property
    def status_dict(self):
        """
        センサの値を表すメンバを辞書として返す。外部からは`センサーインスタンス.status_dict`のように、メンバとして呼び出せる

        Returns
        -------
        status_dict : dict[str, int or str]
            メンバの値の辞書
        """

        def restore(data):
            """
            Synchronized型のデータをPythonで直接扱える形式に復元する

            Parameters
            ----------
            data : multiprocessing.sharedctypes.Synchronized or other(default python type)
                復元したいデータ
            """
            if isinstance(data, Synchronized):
                return data.value
            return data

        return {k: restore(v) for k, v in self.__dict__.items() if not k.startswith("_")}


class Thermistor(I2CSensorBase):
    """
    サーミスターを表すクラス

    Attributes
    ----------
    type : str
        センサーの種類(サーミスター)
    model_number : str
        センサーの型番
    measured_time : multiprocessing.Value("d")
        現在保持しているデータを取得した時間
    temperature_celsius : multiprocessing.Value("d")
        摂氏温度[℃]
    _bus : smbus2.SMBus
        i2cのバス
    _address : int
        そのセンサーのi2cアドレス
    _p : multiprocessing.Process
        センサーの値を取得してメンバを更新していく並列プロセス
    """

    def __init__(self, bus, address):
        """
        センサ情報を登録してから、セットアップとデータ更新プロセスを開始する

        Parameters
        ----------
        _bus : smbus2.SMBus
            i2cのバス
        _address : int
            そのセンサーのi2cアドレス
        _p : multiprocessing.Process
            センサーの値を取得してメンバを更新していく並列プロセス
        """
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
    """
    圧力センサーを表すクラス

    Attributes
    ----------
    type : str
        センサーの種類(圧力センサー)
    model_number : str
        センサーの型番
    measured_time : multiprocessing.Value("d")
        現在保持しているデータを取得した時間
    pressure_hpa : multiprocessing.Value("d")
        圧力[hPa]
    temperature_celsius : multiprocessing.Value("d")
        摂氏温度[℃]
    altitude_meters : multiprocessing.Value("d")
        高度[m]
    _bus : smbus2.SMBus
        i2cのバス
    _address : int
        そのセンサーのi2cアドレス
    _p : multiprocessing.Process
        センサーの値を取得してメンバを更新していく並列プロセス
    """

    def __init__(self, bus, address):
        """
        センサ情報を登録してから、セットアップとデータ更新プロセスを開始する

        Parameters
        ----------
        _bus : smbus2.SMBus
            i2cのバス
        _address : int
            そのセンサーのi2cアドレス
        _p : multiprocessing.Process
            センサーの値を取得してメンバを更新していく並列プロセス
        """
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


class Accelerometer(I2CSensorBase):
    """
    加速度センサーを表すクラス

    Attributes
    ----------
    type : str
        センサーの種類(加速度センサー)
    model_number : str
        センサーの型番
    measured_time : multiprocessing.Value("d")
        現在保持しているデータを取得した時間
    accelerometer_x_mps2 : multiprocessing.Value("d")
        x軸方向の加速度
    accelerometer_y_mps2 : multiprocessing.Value("d")
        y軸方向の加速度
    accelerometer_z_mps2 : multiprocessing.Value("d")
        z軸方向の加速度
    _bus : smbus2.SMBus
        i2cのバス
    _address : int
        そのセンサーのi2cアドレス
    _p : multiprocessing.Process
        センサーの値を取得してメンバを更新していく並列プロセス
    """

    def __init__(self, bus, address):
        """
        センサ情報を登録してから、セットアップとデータ更新プロセスを開始する

        Parameters
        ----------
        _bus : smbus2.SMBus
            i2cのバス
        _address : int
            そのセンサーのi2cアドレス
        _p : multiprocessing.Process
            センサーの値を取得してメンバを更新していく並列プロセス
        """
        self.type = "accelerometer"
        self.model_number = "KX224-1053"
        self.measured_time = Value("d", 0.0)
        self.accelerometer_x_mps2 = Value("d", 0.0)
        self.accelerometer_y_mps2 = Value("d", 0.0)
        self.accelerometer_z_mps2 = Value("d", 0.0)
        super().__init__(bus, address)

    def setup(self):
        pass

    def process(self):
        while True:
            sleep(3)
            self.measured_time.value = time()
            self.accelerometer_x_mps2.value += 1
            self.accelerometer_y_mps2.value += 1
            self.accelerometer_z_mps2.value += 1


class TemperatureHumiditySensor(I2CSensorBase):
    """
    温湿度センサーを表すクラス

    Attributes
    ----------
    type : str
        センサーの種類(温湿度センサー)
    model_number : str
        センサーの型番
    measured_time : multiprocessing.Value("d")
        現在保持しているデータを取得した時間
    temperature_celsius : multiprocessing.Value("d")
        温度[℃]
    humidity_percent : multiprocessing.Value("d")
        空気中の湿度[%]
    _bus : smbus2.SMBus
        i2cのバス
    _address : int
        そのセンサーのi2cアドレス
    _p : multiprocessing.Process
        センサーの値を取得してメンバを更新していく並列プロセス
    """

    def __init__(self, bus, address):
        """
        センサ情報を登録してから、セットアップとデータ更新プロセスを開始する

        Parameters
        ----------
        _bus : smbus2.SMBus
            i2cのバス
        _address : int
            そのセンサーのi2cアドレス
        _p : multiprocessing.Process
            センサーの値を取得してメンバを更新していく並列プロセス
        """
        self.type = "temperature_humidity_sensor"
        self.model_number = "SHT31"
        self.measured_time = Value("d", 0.0)
        self.temperature_celsius = Value("d", 0.0)
        self.humidity_percent = Value("d", 0.0)
        super().__init__(bus, address)

    def setup(self):
        pass

    def process(self):
        while True:
            sleep(0.5)
            self.measured_time.value = time()
            self.temperature_celsius.value += 1
            self.humidity_percent.value += 1

# TODO: 脈波センサークラス


if __name__ == "__main__":
    Th1 = Thermistor("bus", 0x40)
    Th2 = Thermistor("bus", 0x60)
    Pr = PressureSensor("bus", 0x80)
    Ac = Accelerometer("bus", 0xa1)
    while True:
        sleep(1)
        print(Th1.status_dict, Th2.status_dict, Pr.status_dict, Ac.status_dict)
