"""
test_bridge_sensor.py — 原始电桥压力传感器测试 (ADS1115 差分 AIN1-AIN3)

接线 (经验证):
  传感器 VO+ (Pin4) → ADS1115 AIN1
  传感器 VO- (Pin6) → ADS1115 AIN3  (⚠ 不是 Pin1!)
  传感器 VS+ (Pin5) → 5V
  传感器 VS- (Pin2) → GND
  NC     (Pin3)     → 悬空
"""
from machine import I2C, Pin
import time, sys

print("=" * 50)
print("  电桥压力传感器测试 (ADS1115 差分 AIN1-AIN3)")
print("=" * 50)

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
devs = i2c.scan()
if 0x48 not in devs:
    print("❌ 未检测到 ADS1115!"); sys.exit(1)
print(f"✅ ADS1115 @ 0x48")

sys.path.append('')
from lib.ads1115 import ADS1115
ads = ADS1115(i2c, addr=0x48, gain=0.256, sps=860)
print(f"  PGA = ±{ads._pga}V, LSB = {ads.lsb*1e6:.1f} μV\n")

# ---- 差分读取 ----
print("差分电压 (AIN1 - AIN3, ±0.256V):")
print(f"{'raw':>8}  {'mV':>8}")
print("-" * 22)

for _ in range(8):
    raw = ads.read_raw_diff(1, 3, gain=0.256)
    mv = raw * ads.lsb * 1000
    print(f"  {raw:6d}  {mv:8.3f}")
    time.sleep_ms(200)

# ---- 实时监控 ----
print("\n\n实时监控 (捏气嘴看变化, Ctrl+C 退出)")
print(f"{'raw':>8}  {'mV':>8}  {'kPa(估)':>8}")
print("-" * 35)

# 标定值 (基于实测 ~-77mV 零位, 假设 40kPa/70mV)
MV_ZERO = -77.0   # mV, 通大气零位
MV_KPA = 1.75     # mV/kPa (40kPa 传感器 ~70mV FS)

try:
    while True:
        raw = ads.read_raw_diff(1, 3)
        mv = raw * ads.lsb * 1000
        kpa = max(0, (mv - MV_ZERO) / MV_KPA)
        print(f"  {raw:6d}  {mv:8.3f}  {kpa:8.3f}")
        time.sleep_ms(300)
except KeyboardInterrupt:
    print("\n  Done.")
