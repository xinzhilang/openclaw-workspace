"""
test_ads1115.py — ADS1115 模块到货测试

接线:
  ADS1115 VDD → ESP32 3.3V
  ADS1115 GND → ESP32 GND
  ADS1115 SCL → GPIO22
  ADS1115 SDA → GPIO21
  ADS1115 ADDR → GND

测试内容:
  1. I2C 扫描检测
  2. 读取各通道原始值
  3. AIN0 接入 XGZP6847A 时读取电压
"""
from machine import I2C, Pin
import time, sys

print("=" * 44)
print("  ADS1115 模块到货测试")
print("=" * 44)

# ---- 1. I2C 扫描 ----
print("\n[1/4] I2C 总线扫描...")
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
devices = i2c.scan()

if not devices:
    print("  ❌ 无 I2C 设备！检查接线：")
    print("     SDA=GPIO21  SCL=GPIO22")
    print("     VDD→3.3V  GND→GND")
    sys.exit(1)

print(f"  ✅ 检测到设备: {[hex(d) for d in devices]}")

if 0x48 not in devices:
    print("  ❌ ADS1115 未在 0x48！检查 ADDR 引脚")
    print(f"     当前设备: {[hex(d) for d in devices]}")
    sys.exit(1)

print("  ✅ ADS1115 地址 0x48 ✓\n")

# ---- 2. 创建驱动 ----
sys.path.append('')
from lib.ads1115 import ADS1115

ads = ADS1115(i2c, addr=0x48, gain=4.096, sps=860)

print(f"[2/4] 配置:")
print(f"  PGA = ±{ads._pga}V  (LSB = {ads.lsb*1000:.3f} mV)")
print(f"  SPS = {ads._sps}")
print(f"  VDD = {ads._pga / ads.lsb / 2:.3f}V max input\n")

# ---- 3. 各通道轮读 ----
print("[3/4] 各通道电压 (无输入 = 乱飘正常):")
for ch in range(4):
    try:
        v = ads.read_voltage(ch, samples=4)
        raw = ads.read_raw(ch)
        print(f"  AIN{ch}:  raw={raw:6d}  {v*1000:7.2f} mV")
    except Exception as e:
        print(f"  AIN{ch}:  ❌ {e}")
print()

# ---- 4. AIN0 连续监控 (接 XGZP6847A) ----
print("[4/4] AIN0 实时监控 (Ctrl+C 退出)")
print("  " + "-" * 36)
print(f"  {'ADC':>6}  {'mV':>8}  {'kPa(估)':>8}")
print("  " + "-" * 36)

# XGZP6847A 估算参数 (需重新标定)
V_ZERO = 0.115   # 0kPa 电压 (旧标定值, 可能因ADS1115不同)
V_PER_KPA = 0.090  # 每 kPa 电压增量

try:
    while True:
        raw = ads.read_raw(0, samples=4)
        mv = raw * ads.lsb * 1000
        volt = mv / 1000
        kpa = max(0, (volt - V_ZERO) / V_PER_KPA)
        print(f"  {raw:6d}  {mv:8.2f}  {kpa:8.2f}", end="")
        # 噪音指示
        raw2 = ads.read_raw(0, samples=4)
        drift = abs(raw - raw2)
        if drift <= 1:
            print("  ✦ 稳定")
        elif drift <= 3:
            print("  ~ 正常")
        else:
            print(f"  ⚡ 抖动{drift}")
        time.sleep_ms(300)
except KeyboardInterrupt:
    print("\n  Done.")
