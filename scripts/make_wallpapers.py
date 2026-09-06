#!/usr/bin/env python3
"""奶龙主题壁纸生成：原图直出，不抠图、不P图

用法: python3 make_wallpapers.py <表情目录> <输出目录> [宽度] [高度]

原则：能不改原图就不改原图。原图完整等比缩放居中放置，
四周空白用原图自身模糊延伸填充，壁纸内容 100% 来自原图。
"""
import os
import sys

from PIL import Image

EMOTES_DIR = sys.argv[1] if len(sys.argv) > 1 else "emotes"
OUT_DIR = sys.argv[2] if len(sys.argv) > 2 else "wallpaper-out"
W = int(sys.argv[3]) if len(sys.argv) > 3 else 1920
H = int(sys.argv[4]) if len(sys.argv) > 4 else 1080


def fill_color(img, margin=8):
    """背景填充色：白底素材用纯白（与原图无缝），其余用边缘平均色"""
    rgb = img.convert("RGB")
    w, h = img.size

    def bright(px):
        return min(px) > 200

    # 四个角落各取一块采样区，只要有明显白色角落就判定为白底
    c = 12
    for rx, ry in ((0, 0), (w - c, 0), (0, h - c), (w - c, h - c)):
        vals = [rgb.getpixel((min(rx + dx, w - 1), min(ry + dy, h - 1)))
                for dx in range(c) for dy in range(c)]
        if sum(1 for v in vals if bright(v)) >= len(vals) * 0.5:
            return (255, 255, 255)

    # 否则用整圈边缘的平均色
    samples = []
    step = 6
    for x in range(0, w, step):
        samples.append(rgb.getpixel((x, margin)))
        samples.append(rgb.getpixel((x, h - 1 - margin)))
    for y in range(0, h, step):
        samples.append(rgb.getpixel((margin, y)))
        samples.append(rgb.getpixel((w - 1 - margin, y)))
    n = len(samples)
    return tuple(sum(c[i] for c in samples) // n for i in range(3))


def compose_original(emote, out_path):
    """原图直出：原图完整等比缩放居中，背景用原图边缘主色填充"""
    bg = Image.new("RGB", (W, H), fill_color(emote))

    # 原图等比缩放（contain）后居中放置，不做任何裁剪
    ratio = min(W / emote.width, H / emote.height)
    new_w, new_h = max(1, int(emote.width * ratio)), max(1, int(emote.height * ratio))
    sharp = emote.resize((new_w, new_h), Image.LANCZOS)
    bg.paste(sharp, ((W - new_w) // 2, (H - new_h) // 2))

    bg.save(out_path, quality=92)
    print("original:", out_path)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for f in sorted(os.listdir(EMOTES_DIR)):
        if not f.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
            continue
        src = os.path.join(EMOTES_DIR, f)
        try:
            img = Image.open(src)
            img.seek(0)
            img = img.convert("RGB")
        except Exception as e:
            print("skip", f, e)
            continue
        name = os.path.splitext(f)[0]
        out_path = os.path.join(OUT_DIR, f"{name}.jpg")
        compose_original(img, out_path)


if __name__ == "__main__":
    main()
