"""
水路 (HX710B) 标定 — 用气路 (XGZP6847A) 做参考
接线：
  打气筒 → T型三通 ── XGZP6847A (GPIO36)
                      └─ HX710B (GPIO35/5)
"""
from machine import ADC, Pin
import time

# ===== XGZP6847A (参考传感器) =====
class RefSensor:
    def __init__(self, pin=36):
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)
        self.adc.width(ADC.WIDTH_12BIT)
        time.sleep_ms(50)

    def read_kpa(self, samples=16):
        total = 0
        for _ in range(samples):
            total += self.adc.read()
            time.sleep_ms(1)
        v = total / samples / 4095 * 3.3
        # 临时用出厂参数估算
        kpa = (v - 0.115) / 0.090
        return max(0, kpa)

# ===== HX710B (待标定传感器) =====
class CalSensor:
    def __init__(self, dout=35, sck=5):
        self.dout = Pin(dout, Pin.IN)
        self.sck = Pin(sck, Pin.OUT)
        self.sck.value(0)
        self._offset = 2863062  # 从上次水柱法来的

    def _wait(self, timeout_ms=1000):
        t = time.ticks_ms()
        while self.dout.value() == 1:
            if time.ticks_diff(time.ticks_ms(), t) > timeout_ms:
                return False
            time.sleep_ms(1)
        return True

    def read_raw(self):
        if not self._wait():
            return None
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

    def read_tared(self, samples=5):
        vals = []
        for _ in range(samples):
            v = self.read_raw()
            if v is None:
                return None
            vals.append(v)
        vals.sort()
        if len(vals) >= 3:
            vals = vals[1:-1]
        return sum(vals) // len(vals) - self._offset


# ===== 标定 =====
print("=" * 50)
print("  水路标定 — 以气路为参考")
print("=" * 50)
print("气管接三通: XGZP6847A + HX710B + 打气筒\n")

ref = RefSensor()
cal = CalSensor()

print("通大气归零中...")
vals = []
for _ in range(10):
    v = cal.read_tared()
    if v is not None:
        vals.append(v)
    time.sleep_ms(100)
if vals:
    cal._offset = sum(vals) // len(vals) + 2863062  # 修正零位
    print(f"HX710B 零位 Offset: {cal._offset}")

print("\n逐点加压记录 (稳定后按 y + Enter)")
print()

points = []
try:
    while True:
        ref_kpa = ref.read_kpa()
        cal_td = cal.read_tared()
        if cal_td is None:
            cal_td = -99999
        print(f"  气路={ref_kpa:6.2f}kPa  |  水路Tared={cal_td:+8d}  — 按 y: ", end="")
        inp = input().strip().lower()
        if inp == 'y':
            # 多次采样取平均
            r_vals = [ref.read_kpa() for _ in range(5)]
            c_vals = [cal.read_tared() for _ in range(5)]
            c_vals = [v for v in c_vals if v is not None]
            if c_vals:
                r_avg = sum(r_vals) / len(r_vals)
                c_avg = sum(c_vals) // len(c_vals)
                points.append((r_avg, c_avg))
                print(f"  ✅ 参考={r_avg:.2f}kPa  →  HX710B Tared={c_avg:+d}")
                print(f"  已录 {len(points)} 组\n")
except KeyboardInterrupt:
    print("\n\n计算中...\n")

if len(points) < 2:
    print("至少 2 组数据!")
else:
    print("=" * 50)
    print("  标定结果")
    print("=" * 50)
    print(f"{'参考kPa':>10}  {'HX710B Tared':>14}")
    print("-" * 28)

    kpa_v = [p[0] for p in points]
    adc_v = [p[1] for p in points]

    for k, a in points:
        print(f"{k:>10.2f}  {a:+14d}")

    # 线性拟合 Tared → kPa
    n = len(points)
    sum_x = sum(adc_v); sum_y = sum(kpa_v)
    sum_xx = sum(x*x for x in adc_v)
    sum_xy = sum(adc_v[i]*kpa_v[i] for i in range(n))
    denom = n*sum_xx - sum_x*sum_x
    if denom == 0:
        print("数据有误")
    else:
        k = (n*sum_xy - sum_x*sum_y) / denom
        b = (sum_y - k*sum_x) / n
        y_m = sum_y/n
        ss_r = sum((kpa_v[i]-(k*adc_v[i]+b))**2 for i in range(n))
        ss_t = sum((kpa_v[i]-y_m)**2 for i in range(n))
        r2 = 1 - ss_r/ss_t if ss_t else 0

        print(f"\n  转换公式:")
        print(f"  kPa = Tared × {k:.9f} + {b:.6f}")
        print(f"  每 kPa ≈ {1/k:.0f} ADC counts" if k else "")
        print(f"  R² = {r2:.4f}" + ("  ✅" if r2 > 0.99 else ""))

        print(f"\n  >>> 保存到 pressure.py:")
        print(f"  WaterSensor(offset={cal._offset}, scale={k:.9f})")
