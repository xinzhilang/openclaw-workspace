"""
calibrate_ads1115_xgzp.py — ADS1115 + XGZP6847A 联合标定

将 XGZP6847A 的 AOUT 接 ADS1115 AIN0
用打气筒 + 压力表标定

相比 ESP32 ADC，ADS1115 16-bit 精度吊打，标定曲线会漂亮很多
"""
from machine import I2C, Pin
import time, sys

print("=" * 50)
print("  ADS1115 + XGZP6847A 气路标定")
print("=" * 50)
print()

# ---- I2C 初始化 ----
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
devs = i2c.scan()
if 0x48 not in devs:
    print("❌ 未检测到 ADS1115!")
    print(f"  设备: {[hex(d) for d in devs]}")
    sys.exit(1)
print(f"✅ ADS1115 @ 0x48")

sys.path.append('')
from lib.ads1115 import ADS1115
ads = ADS1115(i2c, addr=0x48, gain=6.144, sps=860)

print(f"  PGA = ±{ads._pga}V, SPS = {ads._sps}")
print()

# ---- 零位测量 ----
print("通大气测量零位...")
zero_v = []
for _ in range(20):
    zero_v.append(ads.read_voltage(0))
    time.sleep_ms(100)
zero_volt = sum(zero_v) / len(zero_v)
zero_raw = int(zero_volt / ads.lsb)
print(f"  零位: {zero_raw} counts  =  {zero_volt*1000:.1f} mV\n")

# ---- 逐点标定 ----
points = []
print("接上压力表 + 打气筒")
print("稳定后按 y + Enter\n")

try:
    while True:
        v = ads.read_voltage_avg(0, samples=8)
        raw = int(v / ads.lsb)
        print(f"  当前: raw={raw:6d}  {v*1000:7.2f} mV", end="")
        print("  — 按 y + Enter: ", end="")
        inp = input().strip().lower()
        if inp == 'y':
            vals = [ads.read_voltage(0) for _ in range(10)]
            v_avg = sum(vals) / len(vals)
            raw_avg = int(v_avg / ads.lsb)
            print(f"  压力表读数 (bar, 如 0.05, 0.10...): ", end="")
            bar = float(input().strip())
            kpa = bar * 100
            points.append((bar, kpa, raw_avg, v_avg))
            print(f"  ✅ {bar:.3f} bar ({kpa:.1f} kPa) → raw={raw_avg}  {v_avg*1000:.1f} mV")
            print(f"  已录 {len(points)} 组\n")
except KeyboardInterrupt:
    print("\n\n计算中...\n")

if len(points) < 2:
    print("至少需要 2 组数据!")
else:
    print("=" * 50)
    print("  标定结果")
    print("=" * 50)
    print(f"{'bar':>8}  {'kPa':>8}  {'raw':>6}  {'mV':>8}")
    print("-" * 40)

    raw_v = [p[2] for p in points]
    kpa_v = [p[1] for p in points]
    volt_v = [p[3] for p in points]

    for bar, kpa, raw, v in points:
        print(f"{bar:>8.3f}  {kpa:>8.1f}  {raw:>6}  {v*1000:>7.1f}")

    # ADC raw → kPa
    n = len(points)
    sx = sum(raw_v); sy = sum(kpa_v)
    sxx = sum(x*x for x in raw_v)
    sxy = sum(raw_v[i]*kpa_v[i] for i in range(n))
    d = n*sxx - sx*sx
    if abs(d) > 1e-9:
        k_adc = (n*sxy - sx*sy) / d
        b_adc = (sy - k_adc*sx) / n
        y_m = sy/n
        ss_r = sum((kpa_v[i] - (k_adc*raw_v[i] + b_adc))**2 for i in range(n))
        ss_t = sum((kpa_v[i] - y_m)**2 for i in range(n))
        r2 = 1 - ss_r/ss_t if ss_t else 0
        print(f"\n  📐 raw → kPa:")
        print(f"  kPa = raw × {k_adc:.6f} + {b_adc:.2f}")
        print(f"  R² = {r2:.6f}")

    # Voltage → kPa
    sx2 = sum(volt_v); sy2 = sum(kpa_v)
    sxx2 = sum(v*v for v in volt_v)
    sxy2 = sum(volt_v[i]*kpa_v[i] for i in range(n))
    d2 = n*sxx2 - sx2*sx2
    if abs(d2) > 1e-9:
        k_v = (n*sxy2 - sx2*sy2) / d2
        b_v = (sy2 - k_v*sx2) / n
        print(f"\n  📐 Voltage → kPa:")
        print(f"  kPa = (V - {b_v:.4f}) × {k_v:.1f}")
        print(f"  或: kPa = (V - {zero_volt:.4f}) × {k_v:.1f}  (相对零位)")

    print(f"\n  >>> 写入 pressure.py:")
    print(f"  # ADS1115 + XGZP6847A (AIN0)")
    print(f"  v_zero = {zero_volt:.4f}  # {zero_raw} counts")
    if abs(d2) > 1e-9:
        print(f"  v_kpa  = {1/k_v:.4f}")
