"""
压力传感器标定 — 指针压力表法
接线：OUT=GPIO35, SCK=GPIO5
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
        for _ in range(1):
            self.sck.value(1)
            time.sleep_us(1)
            self.sck.value(0)
            time.sleep_us(1)
        if raw & 0x800000:
            raw -= 0x1000000
        return raw

    def read(self, samples=5):
        vals = [self.read_raw() for _ in range(samples)]
        if samples >= 3:
            vals.sort()
            vals = vals[1:-1]
        return sum(vals) // len(vals)

    def tare(self, samples=10):
        print("归零中（确保传感器通大气）...")
        vals = [self.read() for _ in range(samples)]
        self._offset = sum(vals) // len(vals)
        print(f"归零完成  Offset: {self._offset}\n")

    def get_tared(self):
        """返回归零后的 ADC 值"""
        return self.read() - self._offset


# ========== 标定程序 ==========
print("=" * 42)
print("  压力传感器标定 — 指针压力表法")
print("=" * 42)
print("接线: OUT=GPIO35  SCK=GPIO5\n")

sensor = HX710B(dout_pin=35, sck_pin=5)
sensor.tare()

points = []
print("采样中，按 Ctrl+C 结束并计算结果\n")

try:
    while True:
        # 显示当前实时读数
        tared = sensor.get_tared()
        print(f"  当前 Tared: {tared:+8d}", end="  ")
        print("— 请通入气压，稳定后按 'y' + Enter 记录")
        ans = input()
        if ans.strip().lower() == 'y':
            # 读取 10 次取平均
            vals = [sensor.get_tared() for _ in range(10)]
            avg = sum(vals) // len(vals)
            print(f"  → 记录中... 均值: {avg:+8d}")
            print(f"  请输入压力表读数 (kPa, 比如 5.0): ", end="")
            kpa = float(input().strip())
            points.append((kpa, avg))
            print(f"  ✅ 已记录: {kpa}kPa → ADC {avg:+d}")
            print(f"  当前已录 {len(points)} 组\n")
except KeyboardInterrupt:
    print("\n\n采样结束\n")

# 计算结果
if len(points) < 2:
    print("至少需要 2 组数据才能计算转换系数！")
else:
    print("=" * 42)
    print("  标定结果")
    print("=" * 42)
    print(f"{'压力(kPa)':>10}  {'ADC值':>10}  {'备注':>6}")
    print("-" * 30)
    pk = [p[1] for p in points]
    pp = [p[0] for p in points]

    for i, (kpa, adc) in enumerate(points):
        print(f"{kpa:>10.2f}  {adc:>+10d}")

    # 线性拟合 (最小二乘法)
    n = len(points)
    sum_x = sum(pp)
    sum_y = sum(pk)
    sum_xx = sum(x * x for x in pp)
    sum_xy = sum(pp[i] * pk[i] for i in range(n))

    denom = n * sum_xx - sum_x * sum_x
    if denom == 0:
        print("数据点有问题，无法拟合")
    else:
        k = (n * sum_xy - sum_x * sum_y) / denom   # kPa per ADC count
        b = (sum_y - k * sum_x) / n                  # intercept (should be ~0)
        r2_num = (n * sum_xy - sum_x * sum_y) ** 2
        r2_den = (n * sum_xx - sum_x * sum_x) * (n * sum(y * y for y in pk) - sum_y * sum_y)
        r2 = r2_num / r2_den if r2_den != 0 else 0

        print(f"\n  转换公式:")
        print(f"  kPa = ADC_Tared × {k:.9f} + {b:.6f}")
        print(f"  即 每 kPa ≈ {1/k:.0f} ADC counts" if k != 0 else "")
        print(f"  线性度 R² = {r2:.4f}" + ("  ✅ 线性很好" if r2 > 0.99 else ""))

        print(f"\n  保存到代码里:")
        print(f"  SCALE = {k:.9f}")
        print(f"  OFFSET = {sensor._offset}")
        print(f"  读压力: pressure_kpa = (hx710b.read() - OFFSET) * SCALE")
