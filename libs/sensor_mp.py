# XXX: 変換前のデータの配列を返す__read_datas関数とそれを変換する__convert_[element]関数を実装する
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

    Notes
    -----
    このクラスのサブクラスとしてセンサーを表すクラスを定義する場合、@abstractmethodがついているメソッドのみをオーバーライドすればよいです
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
        self._bus = SMBus(1)
        self._address = address
        self._is_active = Value(c_bool, True)
        try:
            self._setup()
            sleep(1)
        except Exception as e:
            print(type(e), e)
            self._close()
        else:
            self._p = Process(target=self._process, args=())
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
                self._update()
                sleep(1)
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

    def __init__(self, address=0x5C):
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
        self._bus.write_byte_data(self._address, 0x20, 0xC0)  # 25Hz

    def _update(self):
        press, temp = self.__read_datas()

        self.measured_time.value = time()
        self.pressure_hpa.value = self.__convert_pressure(press)
        self.temperature_celsius.value = self.__convert_temperature(temp)
        self.altitude_meters.value = self.__convert_altitude(self.pressure_hpa.value, self.temperature_celsius.value)

    def __read_datas(self):
        datas = [self._bus.read_byte_data(self._address, 0x28 + i) for i in range(5)]
        return datas[0:3], datas[3:5]

    def __convert_pressure(self, data):
        return (data[2] << 16 | data[1] << 8 | data[0]) / 4096

    def __convert_temperature(self, data):
        return 42.5 + ((data[1] << 8 | data[0]) - 65535) / 480

    def __convert_altitude(self, press, temp):
        altimeter_setting_mbar = 1013.25
        return ((pow(press / altimeter_setting_mbar, 0.190263) - 1) * temp) / 0.0065


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

    def __init__(self, address=0x45):
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
        self._bus.write_byte_data(self._address, 0x21, 0x30)

    def _update(self):
        temp, humid = self.__read_datas()

        self.measured_time.value = time()
        self.temperature_celsius.value = self.__convert_temperature(temp)
        self.humidity_percent.value = self.__convert_humidity(humid)

    def __read_datas(self):
        self._bus.write_byte_data(self._address, 0xE0, 0x00)
        datas = self._bus.read_i2c_block_data(self._address, 0x00, 6)
        return (datas[0:2]), (datas[3:5])

    def __convert_temperature(self, data):
        msb, lsb = data
        mlsb = ((msb << 8) | lsb)
        return (-45 + 175 * int(str(mlsb), 10) / (pow(2, 16) - 1))

    def __convert_humidity(self, data):
        msb, lsb = data
        mlsb = ((msb << 8) | lsb)
        return (100 * int(str(mlsb), 10) / (pow(2, 16) - 1))


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

    def _update(self):
        self.measured_time.value = time()
        self.heart_bpm_fifo_1204hz.value += 1
        sleep(10)


if __name__ == "__main__":
    # Th1 = Thermistor(0x40)
    # Th2 = Thermistor(0x60)
    Pr = PressureSensor()
    # Ac = Accelerometer(0xa1)
    THs = TemperatureHumiditySensor()
    # Pw = PulseWaveSensor(0x25)
    while True:
        try:
            sleep(1)
            # print(Th1.status_dict)
            # print(Th2.status_dict)
            print(Pr.status_dict, Pr.is_active)
            # print(Ac.status_dict)
            print(THs.status_dict, THs.is_active)
            # print(Pw.status_dict)
        except KeyboardInterrupt:
            break
