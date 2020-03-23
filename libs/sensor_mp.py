from abc import ABC, abstractmethod
from ctypes import c_bool
from multiprocessing import Process, Value, get_logger
from multiprocessing.sharedctypes import Synchronized
from smbus2 import SMBus
from time import sleep, time
from json import dumps
import logging


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

    Notes
    -----
    このクラスのサブクラスとしてセンサーを表すクラスを定義する場合、@abstractmethodがついているメソッドのみをオーバーライドすればよいです
    """

    @abstractmethod
    def __init__(self, address, logger):
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
        self._logger = logger
        self._is_active = Value(c_bool, True)
        try:
            self._setup()
        except Exception as e:
            print(type(e), e)
            self._close()
        else:
            self._p = Process(name=self.__class__.__name__, target=self._process, args=())
            self._p.start()

    @abstractmethod
    def _setup(self):
        """
        接続前のモード設定などをする
        """
        pass

    @abstractmethod
    def _update(self):
        """
        センサーの値を読みメンバを更新する
        """
        pass

    """
    以下はオーバーライドしない想定のメソッド
    """

    def _process(self):
        """
        センサーの値を取得してメンバを更新するプロセス
        """
        try:
            while self._is_active.value:
                sleep(2)
                self._update()
                self._logger.debug(dumps(self.status_dict, indent=4, separators=(",", ": ")))
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(type(e), e)
        finally:
            self._close()

    def _close(self):
        """
        センサー自体を閉じるメソッド。i2cのバスを閉じて、プロセスの実行も止める
        """
        if isinstance(self._bus, SMBus):
            self._bus.close()
        self._is_active.value = False

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
    _is_active : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        センサが値を更新しているか(問題なく動いているか)
    _p : multiprocessing.Process
        センサーの値を取得してメンバを更新していく並列プロセス
    """

    def __init__(self, address, logger):
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
        super().__init__(address, logger)

    def _setup(self):
        pass

    def _update(self):
        self.measured_time.value = time()
        self.temperature_celsius.value += 1
        sleep(4)


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
    _is_active : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        センサが値を更新しているか(問題なく動いているか)
    _p : multiprocessing.Process
        センサーの値を取得してメンバを更新していく並列プロセス
    """

    def __init__(self, address, logger):
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
        super().__init__(address, logger)

    def _setup(self):
        pass

    def _update(self):
        self.measured_time.value = time()
        self.pressure_hpa.value += 0.1
        self.temperature_celsius.value += 0.1
        self.altitude_meters.value += 0.1
        sleep(2.5)


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
    _is_active : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        センサが値を更新しているか(問題なく動いているか)
    _p : multiprocessing.Process
        センサーの値を取得してメンバを更新していく並列プロセス
    """

    def __init__(self, address, logger):
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
        super().__init__(address, logger)

    def _setup(self):
        pass

    def _update(self):
        self.measured_time.value = time()
        self.accelerometer_x_mps2.value += 1
        self.accelerometer_y_mps2.value += 1
        self.accelerometer_z_mps2.value += 1
        sleep(3)


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
    _is_active : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        センサが値を更新しているか(問題なく動いているか)
    _p : multiprocessing.Process
        センサーの値を取得してメンバを更新していく並列プロセス
    """

    def __init__(self, address, logger):
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
        super().__init__(address, logger)

    def _setup(self):
        pass

    def _update(self):
        self.measured_time.value = time()
        self.temperature_celsius.value += 1
        self.humidity_percent.value += 1
        sleep(0.5)


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
    _is_active : multiprocessing.sharedctypes.Synchronized(ctypes.c_bool)
        センサが値を更新しているか(問題なく動いているか)
    _p : multiprocessing.Process
        センサーの値を取得してメンバを更新していく並列プロセス
    """

    def __init__(self, address, logger):
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
        super().__init__(address, logger)

    def _setup(self):
        pass

    def _update(self):
        self.measured_time.value = time()
        self.heart_bpm_fifo_1204hz.value += 1
        sleep(10)


if __name__ == "__main__":
    logger = get_logger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("[%(asctime)s] %(processName)s %(levelname)s -> %(message)s")
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    fh = logging.FileHandler("a.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    Th1 = Thermistor(0x40, logger)
    Th2 = Thermistor(0x60, logger)
    Pr = PressureSensor(0x80, logger)
    Ac = Accelerometer(0xa1, logger)
    THs = TemperatureHumiditySensor(0x15, logger)
    Pw = PulseWaveSensor(0x25, logger)
    while True:
        try:
            sleep(2)
        except KeyboardInterrupt:
            break
