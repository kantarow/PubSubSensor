#include <Wire.h>
#include "KX224_I2C.h"

float accelerometer_value[3]; //加速度センサの値格納配列
String send_data = "";        //送信データ文字列

KX224 kx224(KX224_DEVICE_ADDRESS_1E);

void setup()
{
  byte rc;
  Serial.begin(9600);
  Wire.begin();
  rc = kx224.init();
  if (rc != 0)
  {
    Serial.println(F("KX224 initialization failed"));
    Serial.flush();
  }
}

void loop()
{
  byte rc;
  rc = kx224.get_val(accelerometer_value);
  //送信文字列をJSON形式にする
  send_data = "{";
  send_data += "\"x\":";
  send_data += String(accelerometer_value[0]);
  send_data += ",\"y\":";
  send_data += String(accelerometer_value[1]);
  send_data += ",\"z\":";
  send_data += String(accelerometer_value[2]);
  send_data += "}";
  Serial.println(send_data.c_str());
}
