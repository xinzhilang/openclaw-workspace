"""蜂鸣器换引脚测试 - 先后试 GPIO17, GPIO16, GPIO4"""
from machine import Pin
import time

for pin in [17, 16, 4]:
    print(f"\n═ 测试 GPIO{pin} ═")
    p = Pin(pin, Pin.OUT, value=0)
    print(f"  GPIO{pin}=LOW (应静音)...")
    time.sleep(1.5)
    
    p.value(1)
    print(f"  GPIO{pin}=HIGH (应响起)...")
    time.sleep(1)
    
    p.value(0)
    print(f"  GPIO{pin}=LOW (应静音)")
    time.sleep(1)

print("\n完毕。哪个脚能听出变化就报给我")
