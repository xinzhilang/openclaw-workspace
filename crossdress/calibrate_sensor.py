from machine import ADC, Pin
import network
import time
import urequests

# ====== WiFi ======
WIFI_SSID = "Xiaomi_6807"
WIFI_PASS = "guochunxi"
DEVICE_URL = "http://192.168.31.151/q"

# ====== ADC初始化 ======
air = ADC(Pin(36))
air.atten(ADC.ATTN_11DB)
air.width(ADC.WIDTH_12BIT)

# ====== 连WiFi ======
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print("连接WiFi...", WIFI_SSID)
wlan.connect(WIFI_SSID, WIFI_PASS)

for i in range(20):
    if wlan.isconnected():
        break
    time.sleep(0.5)
    print(".", end="")

print()
if wlan.isconnected():
    print("✅ IP:", wlan.ifconfig()[0])
else:
    print("❌ WiFi连接失败")
    raise SystemExit

# ====== 读取设备压力 ======
def get_device_kpa():
    try:
        r = urequests.get(DEVICE_URL)
        d = r.json()
        r.close()
        return d.get("ak", None)
    except Exception as e:
        return None

# ====== 标定循环 ======
print("\n=== 气压传感器标定 ===")
print("1. 网页点 ▶ 开始")
print("2. 观察数据对应")
print("3. 充到顶后点 ⏹ 停止\n")

while True:
    raw = air.read()
    v = raw / 4095 * 3.3
    dev = get_device_kpa()

    if dev is not None:
        print(f"传感器:{v:.3f}V  →  设备气压:{dev:>4}kPa")
    else:
        print(f"传感器:{v:.3f}V  →  设备:请求失败", end="")
    time.sleep(1)
