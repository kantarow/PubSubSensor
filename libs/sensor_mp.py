from abc import ABC, abstractmethod
from ctypes import c_bool
from multiprocessing import Process, Value
from multiprocessing.sharedctypes import Synchronized
from smbus2 import SMBus
from time import sleep, time


class I2CSensorBase(ABC):
    """
    I2Cセンサーを表す抽象基底クラス

    Attributes
    ----------
    _bus : smbus2.SMBus
        i2cのバス
    _address : int
        センサーのi2cアドレス
    _is_active : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        センサが値を更新しているか(問題なく動いているか)
    _p : multiprocessing.Process
        センサーの値を取得してメンバを更新していく並列プロセス
    """

    @abstractmethod
    def __init__(self, address):
        """
        センサ情報を登録してから、セットアップとデータ更新プロセスを開始する

        Parameters
        ----------
        _address : int
            センサーのi2cアドレス
        """
        # self._bus = SMBus(1)
        self._bus = "bus"
        self._address = address
        self._is_active = Value(c_bool, True)
        try:
            self._setup()
        except Exception as e:
            print(type(e), e)
            self._close()
        else:
            self._p = Process(target=self._process, args=())
            self._p.start()

    def _close(self):
        if isinstance(self._bus, SMBus):
            self._bus.close()
        self._is_active.value = False

    @abstractmethod
    def _setup(self):
        """
        接続前のモード設定などをする
        """
        pass

    def _process(self):
        """
        センサーの値を取得してメンバを更新するプロセス
        """
        try:
            while self._is_active.value:
                sleep(2)
                self.hoge()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(type(e), e)
        finally:
            self._close()

    @abstractmethod
    def hoge(self):
        """
        センサーの値を読みメンバを更新する
        """
        pass

    @property
    def status_dict(self):
        """
        センサの値を表すメンバを辞書として返す。外部からは`センサーインスタンス.status_dict`のように、メンバとして呼び出せる

        Returns
        -------
        status_dict : dict[str, float or str]
            Publicメンバの値の辞書
        """

        def restore(data):
            """
            Synchronized型のデータをPythonで直接扱える形式に復元する

            Parameters
            ----------
            data : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool) or other(default python type)
                復元したいデータ

            Returns
            -------
            data : float or str
                復元されたデータ、もしくはそのままPythonで扱える型のデータ
            """
            if isinstance(data, Synchronized):
                return data.value
            return data

        return {k: restore(v) for k, v in self.__dict__.items() if not k.startswith("_")}

    @property
    def is_active(self):
        """
        このセンサが動いているかを返す

        Returns
        -------
        self._is_active.value : bool
            _is_activeの値
        """
        return self._is_active.value


class Thermistor(I2CSensorBase):
    """
    サーミスターを表すクラス

    Attributes
    ----------
    type : str
        センサーの種類(サーミスター)
    model_number : str
        センサーの型番
    measured_time : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        現在保持しているデータを取得した時間
    temperature_celsius : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        摂氏温度[℃]
    _bus : smbus2.SMBus
        i2cのバス
    _address : int
        センサーのi2cアドレス
    _p : multiprocessing.Process
        センサーの値を取得してメンバを更新していく並列プロセス
    """

    def __init__(self, address):
        """
        センサ情報を登録してから、セットアップとデータ更新プロセスを開始する

        Parameters
        ----------

        _address : int
            センサーのi2cアドレス
        """
        self.type = "thermistor"
        self.model_number = "103JT-050"
        self.measured_time = Value("d", 0.0)
        self.temperature_celsius = Value("d", 0.0)
        super().__init__(address)

    def _setup(self):
        pass

    def hoge(self):
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
    measured_time : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        現在保持しているデータを取得した時間
    pressure_hpa : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        圧力[hPa]
    temperature_celsius : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        摂氏温度[℃]
    altitude_meters : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        高度[m]
    _bus : smbus2.SMBus
        i2cのバス
    _address : int
        センサーのi2cアドレス
    _p : multiprocessing.Process
        センサーの値を取得してメンバを更新していく並列プロセス
    """

    def __init__(self, address):
        """
        センサ情報を登録してから、セットアップとデータ更新プロセスを開始する

        Parameters
        ----------
        _address : int
            センサーのi2cアドレス
        """
        self.type = "pressure_sensor"
        self.model_number = "LPS251B"
        self.measured_time = Value("d", 0.0)
        self.pressure_hpa = Value("d", 0.0)
        self.temperature_celsius = Value("d", 0.0)
        self.altitude_meters = Value("d", 0.0)
        super().__init__(address)

    def _setup(self):
        pass

    def hoge(self):
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
    measured_time : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        現在保持しているデータを取得した時間
    accelerometer_x_mps2 : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        x軸方向の加速度
    accelerometer_y_mps2 : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        y軸方向の加速度
    accelerometer_z_mps2 : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        z軸方向の加速度
    _bus : smbus2.SMBus
        i2cのバス
    _address : int
        センサーのi2cアドレス
    _p : multiprocessing.Process
        センサーの値を取得してメンバを更新していく並列プロセス
    """

    def __init__(self, address):
        """
        センサ情報を登録してから、セットアップとデータ更新プロセスを開始する

        Parameters
        ----------
        _address : int
            センサーのi2cアドレス
        """
        self.type = "accelerometer"
        self.model_number = "KX224-1053"
        self.measured_time = Value("d", 0.0)
        self.accelerometer_x_mps2 = Value("d", 0.0)
        self.accelerometer_y_mps2 = Value("d", 0.0)
        self.accelerometer_z_mps2 = Value("d", 0.0)
        super().__init__(address)

    def _setup(self):
        pass

    def _process(self):
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
    measured_time : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        現在保持しているデータを取得した時間
    temperature_celsius : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        温度[℃]
    humidity_percent : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        空気中の湿度[%]
    _bus : smbus2.SMBus
        i2cのバス
    _address : int
        センサーのi2cアドレス
    _p : multiprocessing.Process
        センサーの値を取得してメンバを更新していく並列プロセス
    """

    def __init__(self, address):
        """
        センサ情報を登録してから、セットアップとデータ更新プロセスを開始する

        Parameters
        ----------
        _address : int
            センサーのi2cアドレス
        """
        self.type = "temperature_humidity_sensor"
        self.model_number = "SHT31"
        self.measured_time = Value("d", 0.0)
        self.temperature_celsius = Value("d", 0.0)
        self.humidity_percent = Value("d", 0.0)
        super().__init__(address)

    def _setup(self):
        pass

    def _process(self):
        while True:
            sleep(0.5)
            self.measured_time.value = time()
            self.temperature_celsius.value += 1
            self.humidity_percent.value += 1


class PulseWaveSensor(I2CSensorBase):
    """
    脈波センサーを表すクラス

    Attributes
    ----------
    type : str
        センサーの種類(脈波センサー)
    model_number : str
        センサーの型番
    measured_time : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        現在保持しているデータを取得した時間
    heart_bpm_fifo_1204hz : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        脈波の値
    _bus : smbus2.SMBus
        i2cのバス
    _address : int
        センサーのi2cアドレス
    _p : multiprocessing.Process
        センサーの値を取得してメンバを更新していく並列プロセス
    """

    def __init__(self, address):
        """
        センサ情報を登録してから、セットアップとデータ更新プロセスを開始する

        Parameters
        ----------
        _address : int
            センサーのi2cアドレス
        """
        self.type = "pulse_wave_sensor"
        self.model_number = "BH1792GLC"
        self.measured_time = Value("d", 0.0)
        self.heart_bpm_fifo_1204hz = Value("d", 0.0)
        super().__init__(address)

    def _setup(self):
        pass

    def _process(self):
        while True:
            sleep(10)
            self.measured_time.value = time()
            self.heart_bpm_fifo_1204hz.value += 1


if __name__ == "__main__":
    Th1 = Thermistor(0x40)
    # Th2 = Thermistor(0x60)
    Pr = PressureSensor(0x80)
    # Ac = Accelerometer(0xa1)
    # THs = TemperatureHumiditySensor(0x15)
    # Pw = PulseWaveSensor(0x25)
    while True:
        try:
            sleep(1.5)
            print(Th1.status_dict, Th1.is_active)
            print(Pr.status_dict, Pr.is_active)
        except KeyboardInterrupt:
            break
