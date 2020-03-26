# 定義
# アドレス等
SA0_LOW_ADDRESS = 0x5C
SA0_HIGH_ADDRESS = 0x5D
address = SA0_HIGH_ADDRESS

TEST_REG_NACK = -1

LPS25H_WHO_ID = 0xBD

# デバイスタイプ
device_25H = 0
device_auto = 1
device = device_25H

# sa0の状態
sa0_low = 0
sa0_high = 1
sa0_auto = 2

REF_P_XL = 0x08
REF_P_L = 0x09
REF_P_H = 0x0A

WHO_AM_I = 0x0F

RES_CONF = 0x10

CTRL_REG1 = 0x20
CTRL_REG2 = 0x21
CTRL_REG3 = 0x22
CTRL_REG4 = 0x23

STATUS_REG = 0x27

PRESS_OUT_XL = 0x28
PRESS_OUT_L = 0x29
PRESS_OUT_H = 0x2A

TEMP_OUT_L = 0x2B
TEMP_OUT_H = 0x2C

FIFO_CTRL = 0x2E
FIFO_STATUS = 0x2F

RPDS_L = 0x39
RPDS_H = 0x3A

INTERRUPT_CFG = -1
INT_SOURCE = -2
THS_P_L = -3
THS_P_H = -4

LPS25H_INTERRUPT_CFG = 0x24
LPS25H_INT_SOURCE = 0x25
LPS25H_THS_P_L = 0x30
LPS25H_THS_P_H = 0x31
