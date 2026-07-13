# lcd1602.py - I2C LCD1602 驱动
# PCF8574: BL=bit3, E=bit2, RS=bit0, 数据=bit4-7

from machine import I2C
from time import sleep_ms

class LCD1602:
    def __init__(self, i2c, addr=0x27):
        self.i2c = i2c
        self.addr = addr
        self._buf = bytearray(1)
        sleep_ms(100)
        self._init_lcd()

    def _pulse(self, nib, rs=0):
        """写高4位nib到LCD"""
        b = nib | 0x08  # BL=1, E=0
        if rs:
            b |= 0x01   # RS=1 (bit 0)
        self._buf[0] = b
        self.i2c.writeto(self.addr, self._buf)
        self._buf[0] = b | 0x04  # E=1
        self.i2c.writeto(self.addr, self._buf)
        self._buf[0] = b          # E=0
        self.i2c.writeto(self.addr, self._buf)
        sleep_ms(2)

    def _cmd(self, cmd):
        """写指令"""
        self._pulse(cmd & 0xF0, 0)
        self._pulse((cmd << 4) & 0xF0, 0)

    def _data(self, data):
        """写数据"""
        self._pulse(data & 0xF0, 1)
        self._pulse((data << 4) & 0xF0, 1)

    def _init_lcd(self):
        sleep_ms(50)
        # 先确保 E=0, BL=1
        self._buf[0] = 0x08
        self.i2c.writeto(self.addr, self._buf)
        sleep_ms(10)

        # 8bit 复位序列
        self._pulse(0x30, 0); sleep_ms(5)
        self._pulse(0x30, 0); sleep_ms(1)
        self._pulse(0x30, 0); sleep_ms(1)
        self._pulse(0x20, 0); sleep_ms(1)  # 切4bit

        # 4bit 配置
        self._cmd(0x28)  # 4bit 2行
        sleep_ms(1)
        self._cmd(0x0C)  # 显示开, 光标关
        sleep_ms(1)
        self._cmd(0x06)  # 自动右移
        sleep_ms(1)
        self._cmd(0x01)  # 清屏
        sleep_ms(3)

    def clear(self):
        self._cmd(0x01)
        sleep_ms(2)

    def home(self):
        self._cmd(0x02)
        sleep_ms(2)

    def set_cursor(self, col, row):
        addr = col + (0x40 if row else 0x00)
        self._cmd(0x80 | addr)

    def print(self, text):
        for c in text:
            if c == '\n':
                self.set_cursor(0, 1)
            else:
                self._data(ord(c))

    def print_at(self, col, row, text):
        self.set_cursor(col, row)
        self.print(text[:16])
