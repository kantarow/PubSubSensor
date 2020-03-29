class SensorManager:
    """
    センサーを統括してデータをまとめて扱うためのクラス

    Attributes
    ----------
    sensors : tuple[int, Sensor(I2CSensorBase or SerialSensorBase)]
        管理しているセンサーの一覧。それぞれに番号(1-origin)が振られている
    """

    def __init__(self, *sensors):
        self.sensors = []
        for i, sensor in enumerate(sensors, 1):
            self.sensors.append((i, sensor))

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, trace):
        for i, sensor in self.sensors:
            sensor._close()

    def active_sensors(self):
        """
        各センサーが動いているかのタプルを返す

        Returns
        -------
        tuple[bool]
            各センサーのis_activeの値
        """
        return tuple([sensor.is_active for _, sensor in self.sensors])

    @property
    def status_dict(self):
        """
        センサの値を表すメンバを辞書として返す。外部からは`センサーインスタンス.status_dict`のように、メンバとして呼び出せる

        Returns
        -------
        status_dict : dict[str, dict[str, float or str]]
            各センサのstatus_dictの辞書
        """
        return {str(i): sensor.status_dict for i, sensor in self.sensors}
