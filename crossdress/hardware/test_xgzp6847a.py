"""
XGZP6847A 模拟压力传感器测试
接线：VCC→5V(或3.3V), GND→GND, OUT→SVP(GPIO36)
"""
from machine import ADC, Pin
import time

adc = ADC(Pin(36))
adc.atten(ADC.ATTN_11DB)  # 0-3.3V
adc.width(ADC.WIDTH_12BIT)  # 0-4095

print("=== XGZP6847A 压力传感器测试 (v0.16~3.75V → 0~40kPa) ===")
print()

try:
    while True:
        raw = adc.read()
        volt = raw / 4095 * 3.3
        # 根据例程估算 kPa (需标定修正)
        # Voltage_0=0.16V, Voltage_40=3.75V
        # 线性插值
        kpa = (volt - 0.16) / (3.75 - 0.16) * 40
        if kpa < 0:
            kpa = 0
        print(f"  ADC: {raw:4d}  |  {volt:.3f}V  |  ~{kpa:.1f} kPa")
        time.sleep_ms(500)
except KeyboardInterrupt:
    print("\nDone.")
