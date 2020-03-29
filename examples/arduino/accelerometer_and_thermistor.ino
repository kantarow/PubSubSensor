#include <Arduino.h>

//サーミスタ参考: https://nobita-rx7.hatenablog.com/entry/28695194

#include <Wire.h>
#include "KX224_I2C.h"
#include <math.h>

double Vout;                  //出力電圧(Vout)
double R1;                    //サーミスタ抵抗値(R1)
double B;                     //補正係数(B)
double T;                     //サーミスタ温度(T)
double Vout_2;                //出力電圧(Vout)
double R1_2;                  //サーミスタ抵抗値(R1)
double B_2;                   //補正係数(B)
double T_2;                   //サーミスタ温度(T)
float accelerometer_value[3]; //加速度センサの値格納配列

String send_data = ""; //送信データ文字列
char read_data;

KX224 kx224(KX224_DEVICE_ADDRESS_1E);

void setup()
{
    byte rc;
    Serial.begin(9600);
    pinMode(A0, INPUT); //A0番ピンを入力用に設定する
    pinMode(A1, INPUT); //A1番ピンを入力用に設定する
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
    read_data = Serial.read();

    byte rc;
    rc = kx224.get_val(accelerometer_value);
    Vout = analogRead(0) * 5.0 / 1024.0;                    //出力電圧(Vout)を測定
    R1 = (5.0 * 4.7) / Vout - 4.7;                          //サーミスタ抵抗値(R1)を計算
    B = 3452.9 * pow(R1, -0.012329);                        //補正係数(B)を計算
    T = B / log(R1 * exp(B / (25 + 273.15)) / 10) - 273.15; //サーミスタ温度(T)を計算

    Vout_2 = analogRead(1) * 5.0 / 1024.0;                          //出力電圧(Vout)を測定
    R1_2 = (5.0 * 4.7) / Vout_2 - 4.7;                              //サーミスタ抵抗値(R1)を計算
    B_2 = 3452.9 * pow(R1_2, -0.012329);                            //補正係数(B)を計算
    T_2 = B_2 / log(R1_2 * exp(B_2 / (25 + 273.15)) / 10) - 273.15; //サーミスタ温度(T)を計算
    //送信文字列をJSON形式にする
    // send_data = "{";
    // send_data += "\"x\":";
    // send_data += String(accelerometer_value[0]);
    // send_data += ",\"y\":";
    // send_data += String(accelerometer_value[1]);
    // send_data += ",\"z\":";
    // send_data += String(accelerometer_value[2]);
    // send_data += "}";
    //Serial.println(send_data.c_str());
    if (read_data == '1')
    {
        send_data = String(T);
        Serial.println(send_data.c_str());
    }
    else if (read_data == '2')
    {
        send_data = String(T_2);
        Serial.println(send_data.c_str());
    }
    else if (read_data == '5')
    {
        send_data = String(accelerometer_value[0]);
        send_data += ",";
        send_data += String(accelerometer_value[1]);
        send_data += ",";
        send_data += String(accelerometer_value[2]);
        Serial.println(send_data.c_str());
    }
}
