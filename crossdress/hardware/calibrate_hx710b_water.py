"""
压力传感器标定 — 水柱法
接线：OUT=GPIO35, SCK=GPIO5

原理：
  1 m 水柱 ≈ 9.8 kPa
  10 cm 水柱 = 0.98 kPa
"""
from machine import Pin
import time

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
        for _ in range(3):  # Gain 64 = 3 extra pulses (27 total)
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
        print("归零中（传感器通大气）...")
        vals = [self.read() for _ in range(samples)]
        self._offset = sum(vals) // len(vals)
        print(f"归零完成  Offset: {self._offset}\n")

    def get_tared(self):
        return self.read() - self._offset


# ========== 标定 ==========
print("=" * 40)
print("  压力传感器标定 — 水柱法")
print("=" * 40)
print("接好软管（传感器通大气状态）\n")

sensor = HX710B(dout_pin=35, sck_pin=5)
sensor.tare()

print("操作：")
print("1. 将软管末端竖直固定，旁边放尺子")
print("2. 从顶部灌水（用夹子封住管口）")
print("3. 调整水位，稳定后记录\n")

print("  此时软件已归零，按 'y' 记录每个水位\n")

points = []

try:
    while True:
        tared = sensor.get_tared()
        print(f"  当前 Tared: {tared:+8d}  — 稳定后按 y + Enter: ", end="")
        inp = input().strip().lower()
        if inp == 'y':
            vals = [sensor.get_tared() for _ in range(10)]
            avg = sum(vals) // len(vals)
            print(f"  请输入水位高度 (cm): ", end="")
            cm = float(input().strip())
            kpa = cm / 10.2 * 1.0  # 10.2 cm ≈ 1 kPa
            # More precisely: 1 kPa = 10.197 cm H2O
            # So kPa = cm / 10.197
            kpa = cm / 10.197
            points.append((cm, kpa, avg))
            print(f"  ✅ {cm:.0f} cm ({kpa:.2f} kPa) → ADC {avg:+d}")
            print(f"  已录 {len(points)} 组\n")
except KeyboardInterrupt:
    print("\n\n计算中...\n")

if len(points) < 2:
    print("至少 2 组数据!")
else:
    print("=" * 40)
    print("  标定结果")
    print("=" * 40)
    print(f"{'cm':>6}  {'kPa':>8}  {'ADC':>10}")
    print("-" * 28)

    cm_v = [p[0] for p in points]
    kpa_v = [p[1] for p in points]
    adc_v = [p[2] for p in points]

    for cm, kpa, adc in points:
        print(f"{cm:>6.0f}  {kpa:>8.3f}  {adc:+10d}")

    # 最小二乘 ADC → kPa
    n = len(points)
    sum_x = sum(adc_v)
    sum_y = sum(kpa_v)
    sum_xx = sum(x * x for x in adc_v)
    sum_xy = sum(adc_v[i] * kpa_v[i] for i in range(n))

    denom = n * sum_xx - sum_x * sum_x
    if denom == 0:
        print("数据有误")
    else:
        k = (n * sum_xy - sum_x * sum_y) / denom
        b = (sum_y - k * sum_x) / n
        y_mean = sum_y / n
        ss_res = sum((kpa_v[i] - (k * adc_v[i] + b)) ** 2 for i in range(n))
        ss_tot = sum((kpa_v[i] - y_mean) ** 2 for i in range(n))
        r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0

        print(f"\n  转换公式:")
        print(f"  kPa = Tared × {k:.9f} + {b:.6f}")
        print(f"  每 kPa ≈ {1/k:.0f} ADC counts" if k != 0 else "")
        print(f"  R² = {r2:.4f}" + ("  ✅" if r2 > 0.99 else ""))
        print(f"\n  >>> 保存到代码:")
        print(f"  OFFSET = {sensor._offset}")
        print(f"  SCALE  = {k:.9f}")
