"""
lib/calibration.py — 标定参数持久化

保存/加载压力传感器标定系数到 ESP32 内部 flash。
断电不丢，开机自动恢复。

存储位置: /calib.json

自动适配气路/水路传感器类型:
  气路 → AirSensor (v_zero, v_kpa)
  水路 → BridgeSensor (mv_zero, mv_kpa) 或 WaterSensor/HX710B (offset, scale)
"""
import json
import os

# 标定参数保存路径 (ESP32 内部 flash 根目录)
CALIB_PATH = "/calib.json"


def save(air_params: dict, water_params: dict) -> bool:
    """保存标定参数到 flash

    Args:
        air_params:   {"v_zero": float, "v_kpa": float}
        water_params: {"mv_zero": float, "mv_kpa": float}
                      或 {"offset": int, "scale": float}

    文件格式:
        {"air": {...}, "water": {...}, "version": 1}
    """
    data = {
        "version": 1,
        "air": air_params,
        "water": water_params,
    }
    try:
        with open(CALIB_PATH, "w") as f:
            json.dump(data, f)
        print(f"✅ 标定已保存 -> {CALIB_PATH}")
        return True
    except Exception as e:
        print(f"⚠ 保存标定失败: {e}")
        return False


def load():
    """从 flash 加载标定参数

    Returns:
        dict {"air": {...}, "water": {...}} 或 None (无文件/解析失败)
    """
    try:
        with open(CALIB_PATH, "r") as f:
            data = json.load(f)
        print(f"✅ 标定已加载 <- {CALIB_PATH}")
        return data
    except OSError:
        # 文件不存在
        return None
    except Exception as e:
        print(f"⚠ 加载标定失败: {e}")
        return None


def has_calibration() -> bool:
    """检查是否存在标定文件"""
    try:
        os.stat(CALIB_PATH)
        return True
    except OSError:
        return False


def delete():
    """删除已保存的标定"""
    try:
        os.remove(CALIB_PATH)
        print(f"🗑 标定已删除")
        return True
    except Exception as e:
        print(f"⚠ 删除标定失败: {e}")
        return False


# ---- 便捷集成函数 ----

def auto_apply(sensor_air, sensor_water) -> bool:
    """从 flash 加载标定并应用到传感器实例

    Args:
        sensor_air:   AirSensor 实例 (必须有 set_calibration(v_zero, v_kpa))
        sensor_water: BridgeSensor 或 WaterSensor 实例
                      BridgeSensor: set_calibration(mv_zero, mv_kpa)
                      WaterSensor:  set_calibration(offset, scale)

    Returns:
        True=已应用, False=无标定可应用
    """
    data = load()
    if data is None:
        return False

    # ---- 气路 ----
    if "air" in data:
        a = data["air"]
        sensor_air.set_calibration(
            v_zero=a.get("v_zero", 0.030),
            v_kpa=a.get("v_kpa", 0.090),
        )
        print(f"  气路: v_zero={a.get('v_zero'):.3f}V, "
              f"v_kpa={a.get('v_kpa'):.4f}V/kPa")

    # ---- 水路 ----
    if "water" in data:
        w = data["water"]
        # 根据传感器类型自动适配
        if hasattr(sensor_water, "mv_zero"):
            # BridgeSensor (ADS1115 差分)
            sensor_water.set_calibration(
                mv_zero=w.get("mv_zero", 7.0),
                mv_kpa=w.get("mv_kpa", 1.8),
            )
            print(f"  水路(桥式): mv_zero={w.get('mv_zero'):.0f}mV, "
                  f"mv_kpa={w.get('mv_kpa'):.2f}mV/kPa")
        else:
            # WaterSensor (HX710B 数字)
            sensor_water.set_calibration(
                offset=int(w.get("offset", 2863062)),
                scale=w.get("scale", 0.000001314),
            )
            print(f"  水路(HX710B): offset={w.get('offset')}, "
                  f"scale={w.get('scale'):.4e}")

    return True


def auto_save(sensor_air, sensor_water) -> bool:
    """读取当前传感器标定参数并保存到 flash

    Args:
        同上 auto_apply

    Returns:
        True=保存成功
    """
    # 气路
    air_params = {
        "v_zero": sensor_air.v_zero,
        "v_kpa": sensor_air.v_kpa,
    }

    # 水路 — 根据类型提取
    if hasattr(sensor_water, "mv_zero"):
        # BridgeSensor
        water_params = {
            "mv_zero": sensor_water.mv_zero,
            "mv_kpa": sensor_water.mv_kpa,
        }
    else:
        # WaterSensor (HX710B)
        water_params = {
            "offset": sensor_water._offset,
            "scale": sensor_water._scale,
        }

    return save(air_params, water_params)
