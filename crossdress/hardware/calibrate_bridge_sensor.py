"""
calibrate_bridge_sensor.py — 桥式压力传感器 水柱法标定

原理:
  1 m 水柱 ≈ 9.8 kPa
  10 cm 水柱 ≈ 0.98 kPa
  50 cm 水柱 ≈ 4.9 kPa

接线:
  VO+ (Pin4) → AIN1
  VO- (Pin6) → AIN3  (⚠ 不是 Pin1!)
  VS+ (Pin5) → 5V
  VS- (Pin2) → GND

操作方法:
  1. 传感器气嘴接透明软管 (≥60cm)，竖直向上
  2. 从顶部灌水，底部用夹子/打气筒堵住
  3. 不同高度记录差分电压
"""
from machine import I2C, Pin
import time, sys

print("=" * 50)
print("  桥式压力传感器 — 水柱法标定")
print("=" * 50)
print()

# ---- ADS1115 初始化 ----
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
devs = i2c.scan()
if 0x48 not in devs:
    print("❌ 未检测到 ADS1115!")
    sys.exit(1)
print(f"✅ ADS1115 @ 0x48")

sys.path.append('')
from lib.ads1115 import ADS1115
ads = ADS1115(i2c, addr=0x48, gain=0.256, sps=860)
print(f"  PGA = ±{ads._pga}V, LSB = {ads.lsb*1e6:.1f} μV\n")

# ---- 通大气零位 ----
print("通大气测量零位...")
zero_mv = []
for _ in range(20):
    mv = ads.read_diff_voltage(1, 3, gain=0.256) * 1000
    zero_mv.append(mv)
    time.sleep_ms(100)
zero_avg = sum(zero_mv) / len(zero_mv)
print(f"  零位: {zero_avg:.3f} mV\n")

# ---- 逐点标定 ----
points = []
print("软管接传感器，灌水竖起来")
print("稳定后按 y + Enter\n")

try:
    while True:
        mv = ads.read_diff_voltage(1, 3, samples=8, gain=0.256) * 1000
        print(f"  当前: {mv:8.3f} mV", end="")
        print("  — 按 y + Enter: ", end="")
        inp = input().strip().lower()
        if inp == 'y':
            vals = [ads.read_diff_voltage(1, 3, gain=0.256)*1000 for _ in range(10)]
            mv_avg = sum(vals) / len(vals)
            print(f"  水柱高度 (cm, 如 10, 20, 30...): ", end="")
            cm = float(input().strip())
            kpa = cm / 10.2  # 10.2 cm ≈ 1 kPa (精确: 1kPa=10.197cm)
            points.append((cm, kpa, mv_avg))
            print(f"  ✅ {cm:.0f} cm ({kpa:.2f} kPa) → {mv_avg:.3f} mV")
            print(f"  已录 {len(points)} 组\n")
except KeyboardInterrupt:
    print("\n\n计算中...\n")

if len(points) < 2:
    print("至少 2 组数据!")
else:
    print("=" * 50)
    print("  标定结果")
    print("=" * 50)
    print(f"{'cm':>8}  {'kPa':>8}  {'mV':>10}")
    print("-" * 32)

    mV_v = [p[2] for p in points]
    kpa_v = [p[1] for p in points]

    for cm, kpa, mv in points:
        print(f"{cm:>8.1f}  {kpa:>8.2f}  {mv:>10.3f}")

    # 线性拟合 mv → kPa
    n = len(points)
    sx = sum(mV_v); sy = sum(kpa_v)
    sxx = sum(x*x for x in mV_v)
    sxy = sum(mV_v[i]*kpa_v[i] for i in range(n))
    d = n*sxx - sx*sx
    if abs(d) > 1e-9:
        k = (n*sxy - sx*sy) / d
        b = (sy - k*sx) / n
        y_m = sy/n
        ss_r = sum((kpa_v[i] - (k*mV_v[i] + b))**2 for i in range(n))
        ss_t = sum((kpa_v[i] - y_m)**2 for i in range(n))
        r2 = 1 - ss_r/ss_t if ss_t else 0

        print(f"\n  📐 mV → kPa:")
        print(f"  kPa = (mV - {b:.3f}) × {k:.4f}")
        print(f"  R² = {r2:.6f}")

    print(f"\n  >>> 写入 pressure.py BridgeSensor:")
    print(f"  mv_zero = {zero_avg:.2f}  # mV")
    if abs(d) > 1e-9:
        print(f"  mv_kpa  = {1/k:.4f}  # mV/kPa")
    print(f"  或: 量程 {1/k * max(mV_v):.0f} kPa (基于标定点推算)")
