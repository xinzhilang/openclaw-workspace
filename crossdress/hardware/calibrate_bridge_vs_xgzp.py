"""
calibrate_bridge_vs_xgzp.py — 用 XGZP6847A 标定桥式传感器

直接寄存器读写 (不依赖库, 已验证这段代码工作正常)

接线:
  AIN0 ← XGZP6847A
  AIN1-AIN3 ← 新传感器差分 (VO+→AIN1, VO-→AIN3, 5V/GND)

三通: 打气筒 → XGZP → 新传感器
"""
from machine import I2C, Pin
import time, sys

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)

def read_diff_mv():
    """AIN1-AIN3 差分, ±6.144V, 单次, 860SPS
    0xA1: OS=1, MUX=010(AIN1-AIN3), PGA=000(±6.144V), MODE=1
    0xE3: DR=111(860SPS), COMP_DISABLE
    """
    i2c.writeto_mem(0x48, 0x01, b'\xA1\xE3')
    time.sleep_ms(5)
    d = i2c.readfrom_mem(0x48, 0x00, 2)
    raw = (d[0]<<8)|d[1]
    if raw>=0x8000: raw-=0x10000
    return raw * 6144 / 32768

def read_ain0_mv():
    """AIN0 单端, ±6.144V, 单次, 860SPS
    0xC1: OS=1, MUX=100(AIN0-GND), PGA=000(±6.144V), MODE=1
    0xE3: DR=111(860SPS), COMP_DISABLE
    """
    i2c.writeto_mem(0x48, 0x01, b'\xC1\xE3')
    time.sleep_ms(5)
    d = i2c.readfrom_mem(0x48, 0x00, 2)
    raw = (d[0]<<8)|d[1]
    if raw>=0x8000: raw-=0x10000
    return raw * 6144 / 32768

def xgzp_kpa():
    mv = read_ain0_mv()
    return max(0, (mv/1000 - 0.115) / 0.090)

print("=" * 50)
print("  用 XGZP6847A 标定桥式传感器")
print("  裸寄存器, AIN1-AIN3 差分 ±6.144V")
print("=" * 50)

# 通大气零位
print("\n通大气稳定...")
time.sleep(1)
k0 = xgzp_kpa()
m0 = read_diff_mv()
print(f"  通大气:  XGZP={k0:.1f}kPa  桥式={m0:.0f}mV")
print()

# 逐点标定
pts = []
print("三通接打气筒, 稳定后按 y 记录, Ctrl+C 完成\n")

try:
    while True:
        k = xgzp_kpa()
        m = read_diff_mv()
        inp = input(
            f"  XGZP={k:5.1f}kPa  桥式={m:7.0f}mV  → 按 y: ").strip().lower()
        if inp == 'y':
            k_avg = sum(xgzp_kpa() for _ in range(5)) / 5
            m_avg = sum(read_diff_mv() for _ in range(5)) / 5
            pts.append((k_avg, m_avg))
            print(f"  ✅ {len(pts)}: {k_avg:.1f} kPa → {m_avg:.0f} mV\n")
except KeyboardInterrupt:
    print("\n\n计算...")

if len(pts) >= 2:
    print("=" * 50)
    print(f"{'#':>3}  {'kPa':>8}  {'mV':>8}")
    print("-" * 23)
    for i, (k, m) in enumerate(pts, 1):
        print(f"{i:>3}  {k:>8.1f}  {m:>8.1f}")

    x = [p[1] for p in pts]  # mV
    y = [p[0] for p in pts]  # kPa
    n = len(pts)
    sx = sum(x); sy = sum(y)
    sxx = sum(v*v for v in x)
    sxy = sum(x[i]*y[i] for i in range(n))
    d = n*sxx - sx*sx
    if abs(d) > 1e-9:
        kk = (n*sxy - sx*sy) / d
        bb = (sy - kk*sx) / n
        ym = sy/n
        ssr = sum((y[i] - (kk*x[i]+bb))**2 for i in range(n))
        sst = sum((y[i] - ym)**2 for i in range(n))
        r2 = 1 - ssr/sst if sst else 0

        print(f"\n  📐 kPa = (mV - {bb:.1f}) × {kk:.6f}")
        print(f"  R² = {r2:.6f}")
        print(f"\n  >>> pressure.py BridgeSensor:")
        print(f"  mv_zero = {bb:.1f}")
        print(f"  mv_kpa  = {1/kk:.1f}")
else:
    print("不足 2 组")
