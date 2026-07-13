"""
HX710B 压力传感器 — 单文件测试版
接线：
  HX710B VCC → ESP-32S 3.3V
  HX710B END → ESP-32S GND
  HX710B OUT → GPIO35
  HX710B SCK → GPIO5
"""
from machine import Pin
import time

# ========== HX710B 驱动（内嵌） ==========
class HX710B:
    def __init__(self, dout_pin=35, sck_pin=5):
        self.dout = Pin(dout_pin, Pin.IN)
        self.sck = Pin(sck_pin, Pin.OUT)
        self.sck.value(0)
        self._offset = 0

    def _wait_ready(self, timeout_ms=1000):
        start = time.ticks_ms()
        while self.dout.value() == 1:
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                raise TimeoutError("HX710B not ready")
            time.sleep_ms(1)

    def read_raw(self, timeout_ms=1000):
        self._wait_ready(timeout_ms)
        raw = 0
        for _ in range(24):
            self.sck.value(1)
            time.sleep_us(1)
            raw = (raw << 1) | self.dout.value()
            self.sck.value(0)
            time.sleep_us(1)
        # 额外脉冲（通道A/增益128）
        for _ in range(1):
            self.sck.value(1)
            time.sleep_us(1)
            self.sck.value(0)
            time.sleep_us(1)
        # 转有符号24位
        if raw & 0x800000:
            raw -= 0x1000000
        return raw

    def read(self, samples=3):
        vals = [self.read_raw() for _ in range(samples)]
        if samples >= 3:
            vals.sort()
            vals = vals[1:-1]
        return sum(vals) // len(vals)

    def tare(self, samples=10):
        print("归零中，请确保传感器通大气...")
        vals = [self.read() for _ in range(samples)]
        self._offset = sum(vals) // len(vals)
        print(f"归零完成。Offset: {self._offset}")


# ========== 主测试 ==========
print("=== HX710B 压力传感器测试 ===")
print("OUT=GPIO35  SCK=GPIO5")

sensor = HX710B(dout_pin=35, sck_pin=5)
sensor.tare(samples=8)

print("\n每500ms读数 (吹气试效果):")
try:
    while True:
        raw = sensor.read_raw()
        tared = sensor.read() - sensor._offset
        print(f"  RAW: {raw:+8d}  |  Tared: {tared:+8d}")
        time.sleep_ms(500)
except KeyboardInterrupt:
    print("\n测试结束")
