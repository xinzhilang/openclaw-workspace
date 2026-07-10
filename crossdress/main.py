from machine import ADC, Pin
import network
import time
import urequests

# ====== WiFi 配置 ======
WIFI_SSID = "Xiaomi_6807"
WIFI_PASS = "guochunxi"
DEVICE_URL = "http://192.168.31.151/q"

# ====== 引脚 ======
AIR_PIN = 36     # 气路传感器
WATER_PIN = 39   # 水路传感器

# ====== ADC 初始化 ======
air = ADC(Pin(AIR_PIN))
water = ADC(Pin(WATER_PIN))
air.atten(ADC.ATTN_11DB)
water.atten(ADC.ATTN_11DB)
air.width(ADC.WIDTH_12BIT)
water.width(ADC.WIDTH_12BIT)

# ====== 标定参数 ======
AIR_V_ZERO = 1.477       # 气路 0kPa 电压
AIR_V_KPA = 0.00036      # 气路系数 (100kPa量程)

WATER_V_ZERO = 1.478     # 水路 0kPa 电压
WATER_V_KPA = 0.00032    # 水路系数 (40kPa量程)

# ====== 工具函数 ======
def read_v(pin, samples=15):
    """读取ADC电压，多次采样取平均"""
    total = 0
    for _ in range(samples):
        total += pin.read()
        time.sleep_us(500)
    return total / samples / 4095 * 3.3

def voltage_to_kpa(v, v_zero, v_kpa):
    """电压转压力"""
    return max(0, (v - v_zero) / v_kpa)

def read_sensor(pin, v_zero, v_kpa):
    """一步到位：读电压→转压力"""
    v = read_v(pin)
    return voltage_to_kpa(v, v_zero, v_kpa)

def get_device_status():
    """读取灌肠控制器实时状态"""
    try:
        r = urequests.get(DEVICE_URL)
        d = r.json()
        r.close()
        return d
    except:
        return None

# ====== WiFi 连接 ======
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print(f"连接WiFi: {WIFI_SSID}")
    wlan.connect(WIFI_SSID, WIFI_PASS)
    for _ in range(30):
        if wlan.isconnected():
            break
        time.sleep(0.5)
    if wlan.isconnected():
        print(f"✅ 已连接 - IP: {wlan.ifconfig()[0]}")
        return True
    else:
        print("❌ WiFi 连接失败，进入离线模式")
        return False

# ====== 标定模式 ======
def calibrate_sensor(pin, name, samples=50):
    """单传感器标定，返回 (v_zero, v_kpa)"""
    print(f"\n=== {name} 标定 ===")
    print("测零压（通大气）...")
    v0 = read_v(pin, samples)
    print(f"  {name} 零压: {v0:.3f}V")
    
    input("接好管路加压后按 Enter...")
    v1 = read_v(pin, samples)
    dv = v1 - v0
    print(f"  加压后: {v1:.3f}V  (变化 +{dv:.3f}V)")
    
    bar = float(input("指针表多少 bar? "))
    kpa = bar * 100
    v_kpa = dv / kpa

    print(f"\n  {name} 标定结果:")
    print(f"  V_ZERO = {v0:.3f}")
    print(f"  V_KPA  = {v_kpa:.5f}")
    
    return v0, v_kpa

def auto_calibrate_with_device():
    """使用灌肠控制器自动标定两个传感器"""
    if not connect_wifi():
        print("需要WiFi才能自动标定")
        return
    
    v0a = read_v(air, 50)
    v0w = read_v(water, 50)
    print(f"\n零压  气路:{v0a:.3f}V  水路:{v0w:.3f}V")
    print("\n接好气管/水管 → 网页点 ▶ 开始 → 等稳定后 Ctrl+C\n")
    
    da, dw = [], []
    try:
        while True:
            va = read_v(air)
            vw = read_v(water)
            r = urequests.get(DEVICE_URL)
            d = r.json(); r.close()
            ak, wk = d.get("ak",0), d.get("wk",0)
            if ak > 2: da.append((va, ak))
            if wk > 2: dw.append((vw, wk))
            print(f"气路 {va:.3f}V → {ak}kPa  |  水路 {vw:.3f}V → {wk}kPa")
            time.sleep(1)
    except:
        pass
    
    print("\n=== 标定结果 ===")
    if da:
        avg_a = sum((v-v0a)/p for v,p in da) / len(da)
        print(f"气路: V_ZERO={v0a:.3f}  V_KPA={avg_a:.5f}")
    if dw:
        avg_w = sum((v-v0w)/p for v,p in dw) / len(dw)
        print(f"水路: V_ZERO={v0w:.3f}  V_KPA={avg_w:.5f}")

# ====== 主循环 ======
def main():
    online = connect_wifi()
    print("=== 灌肠控制器传感器 ===")
    print(f"气路: {AIR_V_KPA:.5f} kPa/V  |  水路: {WATER_V_KPA:.5f} kPa/V")
    
    while True:
        a = read_sensor(air, AIR_V_ZERO, AIR_V_KPA)
        w = read_sensor(water, WATER_V_ZERO, WATER_V_KPA)
        
        if online:
            dev = get_device_status()
            if dev:
                print(f"气路:{a:5.1f}kPa  水路:{w:5.1f}kPa  |  "
                      f"设备:气{dev.get('ak',0)}kPa 水{dev.get('wk',0)}kPa  {dev.get('msg','')}")
            else:
                print(f"气路:{a:5.1f}kPa  水路:{w:5.1f}kPa  |  设备离线")
        else:
            print(f"气路:{a:5.1f}kPa  水路:{w:5.1f}kPa")
        
        time.sleep(1)

# ====== 入口 ======
if __name__ == "__main__":
    main()
