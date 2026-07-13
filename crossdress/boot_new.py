"""
boot.py — ESP32 启动初始化
"""
import network
import time

WIFI_SSID = "Xiaomi_6807"
WIFI_PASS = "guochunxi"

# 固定IP（避免和灌肠控制器 192.168.31.151 冲突）
ESP_IP = "192.168.31.200"
GATEWAY = "192.168.31.1"
MASK = "255.255.255.0"
DNS = "192.168.31.1"

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.ifconfig((ESP_IP, MASK, GATEWAY, DNS))
    wlan.connect(WIFI_SSID, WIFI_PASS)
    
    for _ in range(30):
        if wlan.isconnected():
            break
        time.sleep(0.5)
    
    if wlan.isconnected():
        print(f"✅ WiFi | IP: {wlan.ifconfig()[0]}")
        return True
    else:
        print("❌ WiFi 连接失败")
        return False

connect()
