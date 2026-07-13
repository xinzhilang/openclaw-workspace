"""
XGZP6847A 气路标定 — 压力表法 (单位: bar)
接线：OUT→SVP(GPIO36)

0-40 kPa = 0-0.4 bar
"""
from machine import ADC, Pin
import time

adc = ADC(Pin(36))
adc.atten(ADC.ATTN_11DB)
adc.width(ADC.WIDTH_12BIT)

print("=" * 44)
print("  XGZP6847A 气路标定 — 指针压力表 (bar)")
print("=" * 44)
print()

# 零位读数
print("通大气测量零位...")
zero_v = []
for _ in range(20):
    zero_v.append(adc.read())
    time.sleep_ms(100)
zero_adc = sum(zero_v) // len(zero_v)
zero_volt = zero_adc / 4095 * 3.3
print(f"  零位: ADC={zero_adc}  {zero_volt:.3f}V\n")

points = []
print("接上压力表 + 打气筒，逐点记录")
print("稳定后按 y + Enter\n")

try:
    while True:
        raw = adc.read()
        volt = raw / 4095 * 3.3
        print(f"  当前 ADC={raw:4d}  {volt:.3f}V  — 按 y + Enter: ", end="")
        inp = input().strip().lower()
        if inp == 'y':
            vals = [adc.read() for _ in range(10)]
            avg = sum(vals) // len(vals)
            volt_avg = avg / 4095 * 3.3
            print(f"  压力表读数 (bar, 如 0.05, 0.10...): ", end="")
            bar = float(input().strip())
            kpa = bar * 100
            points.append((bar, kpa, avg, volt_avg))
            print(f"  ✅ {bar:.3f} bar ({kpa:.1f} kPa) → ADC {avg}  {volt_avg:.3f}V")
            print(f"  已录 {len(points)} 组\n")
except KeyboardInterrupt:
    print("\n\n计算中...\n")

if len(points) < 2:
    print("至少 2 组数据!")
else:
    print("=" * 44)
    print("  标定结果")
    print("=" * 44)
    print(f"{'bar':>8}  {'kPa':>8}  {'ADC':>6}  {'Volt':>8}")
    print("-" * 36)

    adc_v = [p[2] for p in points]
    kpa_v = [p[1] for p in points]
    volt_v = [p[3] for p in points]

    for bar, kpa, adc_val, volt in points:
        print(f"{bar:>8.3f}  {kpa:>8.2f}  {adc_val:>6}  {volt:>8.3f}")

    # ADC → kPa 拟合
    n = len(points)
    sum_x = sum(adc_v); sum_y = sum(kpa_v)
    sum_xx = sum(x*x for x in adc_v)
    sum_xy = sum(adc_v[i]*kpa_v[i] for i in range(n))
    denom = n*sum_xx - sum_x*sum_x
    if denom:
        k_adc = (n*sum_xy - sum_x*sum_y) / denom
        b_adc = (sum_y - k_adc*sum_x) / n
        y_m = sum_y/n
        ss_r = sum((kpa_v[i]-(k_adc*adc_v[i]+b_adc))**2 for i in range(n))
        ss_t = sum((kpa_v[i]-y_m)**2 for i in range(n))
        r2 = 1 - ss_r/ss_t if ss_t else 0

        print(f"\n  📐 ADC → kPa:")
        print(f"  kPa = ADC × {k_adc:.4f} + {b_adc:.2f}")
        print(f"  R² = {r2:.4f}")

    # Voltage → kPa 拟合
    sum_x2 = sum(volt_v); sum_y2 = sum(kpa_v)
    sum_xx2 = sum(v*v for v in volt_v)
    sum_xy2 = sum(volt_v[i]*kpa_v[i] for i in range(n))
    denom2 = n*sum_xx2 - sum_x2*sum_x2
    if denom2:
        k_v = (n*sum_xy2 - sum_x2*sum_y2) / denom2
        b_v = (sum_y2 - k_v*sum_x2) / n

        print(f"  📐 Voltage → kPa:")
        print(f"  kPa = (V - {b_v:.3f}) × {k_v:.2f}")
        print(f"  或: kPa = (V - {zero_volt:.3f}) × {k_v:.2f}  (相对零位)")

    print(f"\n  >>> 保存到 pressure.py:")
    print(f"  # XGZP6847A on GPIO36")
    print(f"  V_ZERO = {zero_volt:.3f}")
    print(f"  KPA_PER_V = {k_v:.2f}" if denom2 else "")
