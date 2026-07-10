"""
压力传感器标定 — 水柱法 (2脉冲 = Gain 32)
接线：OUT=GPIO35, SCK=GPIO5
"""
from machine import Pin
import time

class HX710B:
    def __init__(self, dout_pin=35, sck_pin=5, extra_pulses=2):
        self.dout = Pin(dout_pin, Pin.IN)
        self.sck = Pin(sck_pin, Pin.OUT)
        self.sck.value(0)
        self.extra_pulses = extra_pulses
        self._offset = 0

    def read_raw(self, timeout_ms=1000):
        start = time.ticks_ms()
        while self.dout.value() == 1:
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                raise TimeoutError("HX710B not ready")
            time.sleep_ms(1)
        raw = 0
        for _ in range(24):
            self.sck.value(1)
            time.sleep_us(1)
            raw = (raw << 1) | self.dout.value()
            self.sck.value(0)
            time.sleep_us(1)
        for _ in range(self.extra_pulses):
            self.sck.value(1)
            time.sleep_us(1)
            self.sck.value(0)
            time.sleep_us(1)
        if raw & 0x800000:
            raw -= 0x1000000
        return raw

    def read_avg(self, samples=5):
        vals = [self.read_raw() for _ in range(samples)]
        if samples >= 3:
            vals.sort()
            vals = vals[1:-1]
        return sum(vals) // len(vals)

    def tare(self, samples=10):
        print("归零中（通大气）...")
        vals = [self.read_avg() for _ in range(samples)]
        self._offset = sum(vals) // len(vals)
        print(f"归零完成  Offset: {self._offset}\n")

    def get_tared(self):
        return self.read_avg() - self._offset


print("=" * 40)
print("  HX710B 标定 — 2脉冲 (Gain 32)")
print("  目标量程: 0-40 kPa")
print("=" * 40)
print("接线: OUT=GPIO35  SCK=GPIO5\n")

sensor = HX710B(extra_pulses=2)
sensor.tare()

print("操作：灌水到不同水位，稳定后按 y 记录\n")
points = []

try:
    while True:
        tared = sensor.get_tared()
        print(f"  当前: {tared:+8d}  — 按 y + Enter: ", end="")
        inp = input().strip().lower()
        if inp == 'y':
            vals = [sensor.get_tared() for _ in range(10)]
            avg = sum(vals) // len(vals)
            print(f"  水位 (cm): ", end="")
            cm = float(input().strip())
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

    adc_v = [p[2] for p in points]
    kpa_v = [p[1] for p in points]

    for cm, kpa, adc in points:
        print(f"{cm:>6.0f}  {kpa:>8.3f}  {adc:+10d}")

    n = len(points)
    sum_x = sum(adc_v); sum_y = sum(kpa_v)
    sum_xx = sum(x*x for x in adc_v)
    sum_xy = sum(adc_v[i]*kpa_v[i] for i in range(n))
    denom = n*sum_xx - sum_x*sum_x
    if denom == 0: print("数据有误")
    else:
        k = (n*sum_xy - sum_x*sum_y) / denom
        b = (sum_y - k*sum_x) / n
        y_m = sum_y/n
        ss_r = sum((kpa_v[i]-(k*adc_v[i]+b))**2 for i in range(n))
        ss_t = sum((kpa_v[i]-y_m)**2 for i in range(n))
        r2 = 1 - ss_r/ss_t if ss_t else 0

        print(f"\n  kPa = Tared × {k:.9f} + {b:.6f}")
        print(f"  R² = {r2:.4f}" + ("  ✅" if r2 > 0.99 else ""))

        # 估算满量程
        max_kpa = k * 8388608 + b
        print(f"  估算满量程: ~{max_kpa:.0f} kPa")

        print(f"\n  >>> 保存到代码:")
        print(f"  OFFSET = {sensor._offset}")
        print(f"  SCALE  = {k:.9f}")
