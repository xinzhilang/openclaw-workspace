#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
视频整理 v3 — 交互式OCR分类工具
===================================
流程：
  1) 打开视频，递进截帧（0s→0.1s→0.2s→0.5s→1s→1.5s→2s）
  2) 展示画面 → 你框选标题区域（拖拽矩形）
  3) 仅对框选区域做OCR → 精准识别标题
  4) AND/OR分类 → 重命名 → 移动到子文件夹

操作键：
  Enter      确认当前结果并保存
  R/r        重新框选标题区域
  B/b        切换OCR引擎（本地PaddleOCR ↔ 百度OCR）
  N/n        跳到下一个时间点
  S/s        跳过该视频（保持原名不处理）
  Esc / Q/q  退出程序

依赖：pip install opencv-python requests Pillow
"""

import cv2
import requests
import os
import re
import shutil
import sys
import base64
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ============================ 中文字体 ============================
_CHINESE_FONT_PATH = None
for _ft in [
    r'C:\Windows\Fonts\msyh.ttc',
    r'C:\Windows\Fonts\simhei.ttf',
    r'C:\Windows\Fonts\msyhbd.ttc',
]:
    if os.path.exists(_ft):
        _CHINESE_FONT_PATH = _ft
        break


def draw_text(img, text, pos, color=(0, 255, 0), size=18):
    """在OpenCV图片上绘制中文文字"""
    if _CHINESE_FONT_PATH is None:
        safe = text.encode('ascii', errors='replace').decode()
        cv2.putText(img, safe, pos, cv2.FONT_HERSHEY_SIMPLEX, size/32, color, 1)
        return img
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(rgb)
    draw = ImageDraw.Draw(pil)
    try:
        font = ImageFont.truetype(_CHINESE_FONT_PATH, size)
    except:
        font = ImageFont.load_default()
    draw.text(pos, text, font=font, fill=(color[2], color[1], color[0]))
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


# ============================ 百度OCR ============================
BAIDU_API_KEY = 'qVi0Ux3koMk5xRhRCInL018r'
BAIDU_SECRET_KEY = 'AFIZprSQxNLR6LdbtLa5BSuYYyWPsscP'
_BAIDU_TOKEN = None


def _baidu_get_token():
    global _BAIDU_TOKEN
    if _BAIDU_TOKEN:
        return _BAIDU_TOKEN
    try:
        r = requests.post(
            'https://aip.baidubce.com/oauth/2.0/token',
            params={'grant_type': 'client_credentials',
                    'client_id': BAIDU_API_KEY,
                    'client_secret': BAIDU_SECRET_KEY},
            timeout=10)
        if r.status_code == 200:
            _BAIDU_TOKEN = r.json().get('access_token')
            return _BAIDU_TOKEN
    except Exception as e:
        print(f"  [!] 百度token获取失败: {e}")
    return None


def baidu_ocr(image_bytes):
    token = _baidu_get_token()
    if not token:
        return None
    try:
        # 图片需要base64编码
        b64 = base64.b64encode(image_bytes).decode('utf-8')
        r = requests.post(
            'https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic',
            params={'access_token': token},
            data={'image': b64, 'language_type': 'CHN_ENG'},
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30)
        if r.status_code == 200:
            d = r.json()
            if 'error_code' in d:
                print(f"  [!] 百度OCR API错误: {d.get('error_msg', d)}")
                return None
            if 'words_result' in d:
                return [w['words'] for w in d['words_result']]
        else:
            print(f"  [!] 百度OCR HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"  [!] 百度OCR失败: {e}")
    return None


# ============================ 配置 ============================
OCR_URL = 'http://localhost:8866/ocr'
FRAME_POINTS_MS = [0, 100, 200, 500, 1000, 1500, 2000]
MIN_TEXT_LENGTH = 4

WATERMARK_KEYWORDS = [
    '无他相机', '美颜相机', 'beautycam', '抖音', '小抖章',
    '万兴喵影', '剪映', 'capcut',
    '辣逼小新', 'labixiaoxin', 'secaishen', '@secaishen',
    'jianjiclub', 'shufuayi',
    '深绿心理研究员', '深绿水岸', 'lvmaosilence', 'qiqubaike',
    'sifangtv.net', 'sifangktv.com', '9p69.com', '宅b-tbar',
    't.me/', 'onlyfans.com', '@labixiaoxin', '@深绿水岸', '@qiqubaike',
    '更多原创视频进',
]

CATEGORY_RULES = [
    (['绿帽', '绿奴'], '老婆·出轨', 'any'),
    (['骚麦', '骚麦系列'], '系列·骚麦', 'any'),
    (['系列·反差', '反差系列'], '系列·反差', 'any'),
    (['女儿', '继女', '干女儿'], '女儿·综合', 'any'),
    (['女友', '女朋友', '女票'], '女友·综合', 'any'),
    (['妈妈', '乱伦'], '妈妈·乱伦', 'all'),
    (['妈妈', '不伦'], '妈妈·乱伦', 'all'),
    (['妈妈', '儿子'], '妈妈·乱伦', 'all'),
    (['母子'], '妈妈·乱伦', 'any'),
    (['妈妈', '教师'], '妈妈·教师', 'all'),
    (['妈妈', '老师'], '妈妈·教师', 'all'),
    (['妈妈', '课堂'], '妈妈·教师', 'all'),
    (['媚黑'], '妈妈·媚黑', 'any'),
    (['妈妈', '黑'], '妈妈·媚黑', 'all'),
    (['妈妈', '反差'], '妈妈·反差', 'all'),
    (['妈妈', '婊'], '妈妈·反差', 'all'),
    (['骚妈', '骚母', '骚妈妈', '操妈', '干妈', '性感的妈妈', '大奶妈', '骚货妈妈'], '妈妈·骚母', 'any'),
    (['妈妈', '老妈', '母亲', '亲妈', '母'], '妈妈·综合', 'any'),
    (['老婆', '出轨'], '老婆·出轨', 'all'),
    (['老婆', '绿帽'], '老婆·出轨', 'all'),
    (['老婆', '偷情'], '老婆·出轨', 'all'),
    (['老婆', '奸夫'], '老婆·出轨', 'all'),
    (['老婆', '别人'], '老婆·出轨', 'all'),
    (['老婆', '调教'], '老婆·调教', 'all'),
    (['老婆', '黑'], '老婆·媚黑', 'all'),
    (['老婆', '反差'], '老婆·反差婊', 'all'),
    (['老婆', '婊'], '老婆·反差婊', 'all'),
    (['淫妻', '淫娃'], '老婆·反差婊', 'any'),
    (['喷水', '潮吹', '吹潮'], '老婆·喷水', 'any'),
    (['露出', '户外', '公园', '野外', '外射', '地铁', '公交车', '公共场所', '大街', '街上'], '老婆·露出', 'any'),
    (['老婆', '娇妻', '人妻', '少妇', '熟女'], '老婆·综合', 'any'),
    (['母女', '妈妈和女儿'], '母女·综合', 'any'),
    (['抖音', '快手', '手冲', '骚舞', '擦玻璃', '跳', '舞', '摇', '卖骚'], '其他·抖音风', 'any'),
    (['反差', '前后', '变身'], '其他·反差', 'any'),
    (['姐妹', '闺蜜', '朋友', '好姐妹'], '其他·姐妹', 'any'),
    (['多人', '群P', '群交', '3p', '4p', 'np', 'party', '派对', '一起'], '其他·多人', 'any'),
    (['刺激', '直播', '自拍', '偷拍', '诱惑', '勾引'], '其他·综合', 'any'),
]

_EPISODE_RE = re.compile(
    r'^(第?[上下中]集|第\d+集|Part\d*|EP\d*|\d+集|'
    r'[\(（][一二三四五六七八九十\d]+[\)）]|'
    r'^[一二三四五六七八九十]?)$', re.IGNORECASE)
INVALID_CHARS = re.compile(r'[<>:"/\\|?*]')
DATE_PREFIX = re.compile(r'^\d{4}\.\d{1,2}\.\d{1,2}\s*')


def is_watermark(text):
    tl = text.lower().replace(' ', '')
    return any(w.lower() in tl for w in WATERMARK_KEYWORDS)


def clean_text(text):
    text = DATE_PREFIX.sub('', text).strip()
    text = INVALID_CHARS.sub('', text)
    return text[:60].strip() if len(text) > 60 else text.strip()


def categorize(text):
    tl = text.lower()
    for kws, cat, mode in CATEGORY_RULES:
        if mode == 'any':
            for kw in kws:
                if kw.lower() in tl:
                    return cat
        elif mode == 'all':
            if all(kw.lower() in tl for kw in kws):
                return cat
    return None


def extract_frame_at(path, ms):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return None, False
    cap.set(cv2.CAP_PROP_POS_MSEC, ms)
    ret, frame = cap.read()
    if not ret and ms > 0:
        cap.set(cv2.CAP_PROP_POS_MSEC, 0)
        ret, frame = cap.read()
    cap.release()
    return frame, ret


def _filter_ocr_texts(texts):
    meaningful = []
    for t in texts:
        ct = t.strip()
        if len(ct) < MIN_TEXT_LENGTH:
            if not _EPISODE_RE.match(ct):
                continue
        if re.match(r'^[\d\s\.\-:年月日时分秒]+$', ct):
            continue
        if is_watermark(ct):
            continue
        if re.match(r'^[a-zA-Z\s]+$', ct):
            continue
        meaningful.append(ct)
    return ''.join(meaningful) if meaningful else None


def roi_ocr(frame, x, y, w, h, use_baidu=False):
    if w <= 0 or h <= 0:
        return None
    roi = frame[y:y+h, x:x+w]
    _, buf = cv2.imencode('.jpg', roi, [cv2.IMWRITE_JPEG_QUALITY, 95])
    img_bytes = buf.tobytes()

    if use_baidu:
        texts = baidu_ocr(img_bytes)
        return _filter_ocr_texts(texts) if texts else None

    try:
        r = requests.post(OCR_URL, files={'file': ('roi.jpg', img_bytes, 'image/jpeg')}, timeout=30)
        if r.status_code == 200:
            d = r.json()
            if d['status'] == 'ok' and d.get('texts'):
                return _filter_ocr_texts(d['texts'])
    except Exception:
        pass
    return None


# ============================ 交互主流程 ============================

_DRAG_START = None
_DRAG_END = None
_CURRENT_DRAG_RECT = None

def _mouse_callback(event, x, y, flags, param):
    global _DRAG_START, _DRAG_END, _CURRENT_DRAG_RECT
    if event == cv2.EVENT_LBUTTONDOWN:
        _DRAG_START = (x, y)
        _CURRENT_DRAG_RECT = None
    elif event == cv2.EVENT_MOUSEMOVE and _DRAG_START:
        _CURRENT_DRAG_RECT = (_DRAG_START[0], _DRAG_START[1], x - _DRAG_START[0], y - _DRAG_START[1])
    elif event == cv2.EVENT_LBUTTONUP:
        _DRAG_END = (x, y)


def _select_roi(frame, ms=0, hint=''):
    """自定义框选，支持 Enter:确认  S:跳过文件  C:下一帧  Esc:退出"""
    global _DRAG_START, _DRAG_END, _CURRENT_DRAG_RECT
    h, w = frame.shape[:2]
    show_w, show_h = 1400, 900
    scale = min(show_w / w, show_h / h)
    dw, dh = int(w * scale), int(h * scale)

    label = f"[{ms}ms] 拖拽框选  Enter确认  S跳过文件  C下一帧  Esc退出"
    if hint:
        label = f"[{ms}ms] {hint} 拖拽框选  Enter确认  S跳过文件  C下一帧"

    cv2.namedWindow('SEL', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('SEL', dw, dh)
    cv2.setMouseCallback('SEL', _mouse_callback)

    _DRAG_START = _DRAG_END = _CURRENT_DRAG_RECT = None
    base = cv2.resize(frame.copy(), (dw, dh))
    base = draw_text(base, label, (10, 30), (0, 255, 0), 18)

    while True:
        disp = base.copy()
        if _CURRENT_DRAG_RECT:
            x, y, rw, rh = _CURRENT_DRAG_RECT
            cv2.rectangle(disp, (x, y), (x+rw, y+rh), (0, 255, 0), 2)
        cv2.imshow('SEL', disp)
        k = cv2.waitKey(30) & 0xFF

        if _DRAG_START and _DRAG_END:
            x1, y1 = _DRAG_START
            x2, y2 = _DRAG_END
            rx, ry = min(x1, x2), min(y1, y2)
            rw, rh = abs(x2 - x1), abs(y2 - y1)
            if rw > 5 and rh > 5:
                # 显示半透明确认画面
                confirm = base.copy()
                cv2.rectangle(confirm, (rx, ry), (rx+rw, ry+rh), (0, 255, 0), 2)
                confirm = draw_text(confirm, 'Enter确认  R重选  S跳过文件  C下一帧  Esc退出',
                                    (10, h-30), (255, 255, 0), 16)
                while True:
                    cv2.imshow('SEL', confirm)
                    k2 = cv2.waitKey(0) & 0xFF
                    if k2 == 13 or k2 == ord(' '):
                        _DRAG_START = _DRAG_END = _CURRENT_DRAG_RECT = None
                        cv2.destroyWindow('SEL')
                        return (int(rx/scale), int(ry/scale),
                                int(rw/scale), int(rh/scale), scale)
                    elif k2 == ord('r') or k2 == ord('R'):
                        _DRAG_START = _DRAG_END = _CURRENT_DRAG_RECT = None
                        break  # 重新框选
                    elif k2 == ord('s') or k2 == ord('S'):
                        _DRAG_START = _DRAG_END = _CURRENT_DRAG_RECT = None
                        cv2.destroyWindow('SEL')
                        return 'SKIP'
                    elif k2 == ord('c') or k2 == ord('C'):
                        _DRAG_START = _DRAG_END = _CURRENT_DRAG_RECT = None
                        cv2.destroyWindow('SEL')
                        return None
                    elif k2 == 27 or k2 == ord('q') or k2 == ord('Q'):
                        sys.exit(0)
            _DRAG_START = _DRAG_END = None

        if k == ord('c') or k == ord('C'):
            _DRAG_START = _DRAG_END = _CURRENT_DRAG_RECT = None
            cv2.destroyWindow('SEL')
            return None
        elif k == ord('s') or k == ord('S'):
            _DRAG_START = _DRAG_END = _CURRENT_DRAG_RECT = None
            cv2.destroyWindow('SEL')
            return 'SKIP'
        elif k == 27 or k == ord('q') or k == ord('Q'):
            sys.exit(0)


def _show_and_wait(frame, lines):
    h, w = frame.shape[:2]
    show_w, show_h = 1400, 900
    scale = min(show_w / w, show_h / h)
    dw, dh = int(w * scale), int(h * scale)
    disp = cv2.resize(frame.copy(), (dw, dh))
    for text, pos, color, font_size in lines:
        disp = draw_text(disp, text, pos, color, font_size)
    cv2.namedWindow('WIN', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('WIN', dw, dh)
    cv2.imshow('WIN', disp)
    k = cv2.waitKey(0) & 0xFF
    cv2.destroyWindow('WIN')
    return k


def process_file(fp, src_dir):
    for ms in FRAME_POINTS_MS:
        frame, ok = extract_frame_at(fp, ms)
        if not ok or frame is None:
            continue
        h, w = frame.shape[:2]

        use_baidu = False
        # 当前时间点的完整处理循环（支持R重选从头开始）
        while True:
            # === 框选ROI ===
            rr = _select_roi(frame, ms, '百度' if use_baidu else '')
            if rr == 'SKIP':
                print("  跳过")
                return None  # 跳过整个文件
            if rr is None:
                break  # 跳过当前ms，尝试下一个
            ox, oy, ow, oh, _ = rr

            # === OCR识别 ===
            text = roi_ocr(frame, ox, oy, ow, oh, use_baidu=use_baidu)
            engine = '百度OCR' if use_baidu else '本地OCR'
            c = (255, 0, 255) if use_baidu else (0, 255, 0)

            if not text:
                k = _show_and_wait(frame, [
                    (f"{engine}未识别到文字", (10, 30), (0, 0, 255), 22),
                    ('N:下一帧  B:切换引擎  R:重选区域  S:跳过  Esc:退出',
                     (10, h-40), (255, 255, 0), 16),
                ])
                if k == ord('n') or k == ord('N'): break
                elif k == ord('b') or k == ord('B'):
                    use_baidu = not use_baidu
                    continue  # 重选+重试
                elif k == ord('r') or k == ord('R'):
                    continue  # 重新框选
                elif k == ord('s') or k == ord('S'): return None
                elif k == 27 or k == ord('q') or k == ord('Q'): sys.exit(0)
                continue

            cleaned = clean_text(text)
            if not cleaned or len(cleaned) < MIN_TEXT_LENGTH:
                continue
            cat = categorize(cleaned) or '其他·综合'

            # === 显示结果，等待确认 ===
            res = frame.copy()
            cv2.rectangle(res, (ox, oy), (ox+ow, oy+oh), c, 2)
            k = _show_and_wait(res, [
                (f'{engine}: {cleaned}  |  分类: {cat}', (10, 30), c, 22),
                ('Enter:确认  R:重选  B:切换引擎  N:下一帧  S:跳过  Esc:退出',
                 (10, h-40), (255, 255, 0), 16),
            ])

            if k == 13 or k == ord(' '):
                new_name = f"{cleaned}.mp4"
                td = os.path.join(src_dir, cat)
                os.makedirs(td, exist_ok=True)
                tp = os.path.join(td, new_name)
                if os.path.exists(tp):
                    base, ext = os.path.splitext(new_name)
                    i = 1
                    while os.path.exists(os.path.join(td, f"{base}({i}){ext}")):
                        i += 1
                    tp = os.path.join(td, f"{base}({i}){ext}")
                shutil.move(fp, tp)
                print(f"  OK {engine} -> {cat}/{os.path.basename(tp)}")
                return tp
            elif k == ord('r') or k == ord('R'):
                continue  # 回到while顶部重新框选
            elif k == ord('b') or k == ord('B'):
                use_baidu = not use_baidu
                continue  # 切换引擎后重新框选
            elif k == ord('n') or k == ord('N'):
                break
            elif k == ord('s') or k == ord('S'):
                return None
            elif k == 27 or k == ord('q') or k == ord('Q'):
                sys.exit(0)
    return None


# ============================ 主函数 ============================

def main():
    print("=" * 65)
    print("  视频整理 v3 — 交互式OCR分类(本地/百度)  操作键")
    print("   Enter:确认  R:重选  B:切换OCR  N:下一帧  S:跳过  Esc/Q:退出")
    print("=" * 65)

    # 检查OCR服务
    try:
        requests.get('http://localhost:8866/health', timeout=5)
        print("[OK] 本地PaddleOCR服务正常")
    except:
        print("[!] 本地PaddleOCR未启动！但百度OCR仍可用")
    print("[OK] 百度OCR已配置\n")

    # 选择目录
    default_dir = r'E:\已整理\剪辑\剪辑\妈妈'
    print(f"目标目录（直接Enter使用默认）:")
    src = input(f"  [{default_dir}]: ").strip() or default_dir

    if not os.path.isdir(src):
        print(f"[!] 目录不存在: {src}")
        input("按Enter退出...")
        return

    files = sorted([os.path.join(src, f) for f in os.listdir(src)
                    if os.path.isfile(os.path.join(src, f)) and f.lower().endswith('.mp4')])
    if not files:
        print("没有待处理的视频文件")
        input("按Enter退出...")
        return

    print(f"\n待处理: {len(files)} 个文件\n")

    renamed = 0
    kept = 0
    for i, fp in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] {os.path.basename(fp)[:70]}")
        print("-" * 65)
        if process_file(fp, src):
            renamed += 1
        else:
            kept += 1

    print(f"\n{'=' * 65}")
    print(f"  完成: 处理 {renamed} 个, 跳过 {kept} 个")
    print(f"\n各分类统计:")
    total = 0
    for d in sorted(os.listdir(src)):
        dp = os.path.join(src, d)
        if os.path.isdir(dp):
            cnt = len([x for x in os.listdir(dp) if x.endswith('.mp4')])
            if cnt:
                print(f"  {d}: {cnt}")
                total += cnt
    root = [f for f in os.listdir(src) if os.path.isfile(os.path.join(src, f)) and f.endswith('.mp4')]
    if root:
        print(f"  (根目录): {len(root)}")
    print(f"  总计: {total + len(root)}")
    print("\n处理完毕！")
    input("按Enter退出...")


if __name__ == '__main__':
    main()
