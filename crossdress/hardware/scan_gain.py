"""
HX710B 增益扫描 — 找适合 0-40 kPa 的脉冲数
接线：OUT=GPIO35, SCK=GPIO5

测试 4 种脉冲方案，在通大气的同一条件下读数对比
"""
from machine import Pin
import time

class HX710B:
    def __init__(self, dout_pin=35, sck_pin=5, extra_pulses=1):
        self.dout = Pin(dout_pin, Pin.IN)
        self.sck = Pin(sck_pin, Pin.OUT)
        self.sck.value(0)
        self.extra_pulses = extra_pulses  # 1, 2, 3, 4

    def read_raw(self, timeout_ms=1000):
        start = time.ticks_ms()
        while self.dout.value() == 1:
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                return None
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
        if None in vals:
            return None
        vals.sort()
        if len(vals) >= 3:
            vals = vals[1:-1]
        return sum(vals) // len(vals)


print("=" * 50)
print("  增益扫描 — 找适合 0-40 kPa 的脉冲数")
print("=" * 50)
print("所有测试均在通大气（0 kPa）下进行\n")

# 测试 4 种脉冲数（通大气读数 + 5kPa加压读数）
pulse_options = [
    (1,  "Gain 128 (最高灵敏度)"),
    (3,  "Gain 64"),
    (2,  "Gain 32"),
    (4,  "最低增益"),
]

print(f"{'脉冲':>6}  {'增益说明':<22}  {'通大气读数':>12}")
print("-" * 50)

results = []

for extra, label in pulse_options:
    s = HX710B(extra_pulses=extra)
    time.sleep_ms(100)  # 等待切换稳定

    # 通大气读数
    vals = []
    for _ in range(5):
        v = s.read_avg(3)
        if v is not None:
            vals.append(v)
        time.sleep_ms(200)

    if not vals:
        print(f"{extra:>6}  {label:<22}  {'无响应':>12}")
        continue

    avg = sum(vals) // len(vals)
    results.append((extra, label, avg))
    print(f"{extra:>6}  {label:<22}  {avg:+12d}")

# 分析
print("\n" + "=" * 50)
print("  分析：哪个适合 40 kPa？")
print("=" * 50)
print("")

# 假设我们观测的是 K 这个芯片的特性
# ADC 最大范围 ±8388608
max_adc = 8388608

for extra, label, zero_val in results:
    # 保守估算：量程 = max_adc / |zero_val| * 0kPa
    # 实际上我们不知道对应关系，但我们知道
    # Gain 128 下 7 kPa ≈ 4.5M counts, 零位 ≈ 2.86M
    # 所以 4.5M counts 对应 7 kPa
    
    # 基于 Gain 128 的校准结果推算
    if extra == 1:
        # 已知: 7 kPa ≈ 4.5M tared counts
        range_kpa = max_adc * 7 / 4500000
        print(f"  Gain 128 (1脉冲):  满量程 ≈ {range_kpa:.0f} kPa  ❌ 不够40kPa")
    elif extra == 3:
        # Gain 64: 敏感度减半, 量程翻倍
        range_kpa = max_adc * 7 * 2 / 4500000
        print(f"  Gain 64  (3脉冲):  满量程 ≈ {range_kpa:.0f} kPa  ❌ 仍然不够")
    elif extra == 2:
        # Gain 32: 敏感度再减半 (相对Gain128 = 1/4)
        range_kpa = max_adc * 7 * 4 / 4500000
        print(f"  Gain 32  (2脉冲):  满量程 ≈ {range_kpa:.0f} kPa  ⚠️ 差不多")
    elif extra == 4:
        # 最低增益: 假设 Gain 16 (相对Gain128 = 1/8)
        range_kpa = max_adc * 7 * 8 / 4500000
        print(f"  最低增益(4脉冲):  满量程 ≈ {range_kpa:.0f} kPa  ✅ 可能够")

print("\n👉 建议：哪个脉冲数的通大气读数最接近 0，就用哪个")
print("   然后用水柱法重新标定！")
