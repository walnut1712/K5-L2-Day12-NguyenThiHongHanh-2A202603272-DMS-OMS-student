#!/usr/bin/env python3
"""Put each SVIRO scene's RGB and IR-sim images side by side and measure what each one shows.

  python3 rgb_ir_diff.py ../data/sviro/set1 --out ir_pairs   [--gamma 2.2]

For every S##_rgb.png / S##_ir.png pair it writes:
  ir_pairs/S##_pair.png   [RGB | RGB brightened | IR-sim], with the left/middle/right rear-seat thirds marked
  ir_pairs/ir_pairs.csv   per image and per third: mean brightness, contrast (std), % near-black, % saturated

Use it to support the ir_log observations (E4). The numbers point to where to look; they do not
decide whether an attribute is visible. Your own judgement does, written in ir_log with the scene id.
SVIRO IR-sim is a red-lamp imitation, not real NIR: falloff with distance, glasses glare and the pupil
effects of real 850/940 nm cameras (slide 22) are not reproduced faithfully. Check those on the real IR
frames (D##, Drive&Act NIR), not here.
"""
import argparse
import csv
import glob
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

DARK, SAT = 16, 250  # 8-bit thresholds for near-black / saturated pixels


def stats(gray):
    return {"mean": float(gray.mean()), "std": float(gray.std()),
            "pct_dark": float((gray < DARK).mean() * 100), "pct_sat": float((gray > SAT).mean() * 100)}


def to_gray(img):
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def brighten(img, gamma):
    a = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    return Image.fromarray(np.clip((a ** (1.0 / gamma)) * 255, 0, 255).astype(np.uint8))


def label(im, text):
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 8 * len(text) + 8, 16], fill=(0, 0, 0))
    d.text((4, 2), text, fill=(255, 255, 0))
    w, h = im.size
    for k in (1, 2):
        d.line([(w * k // 3, 18), (w * k // 3, h)], fill=(0, 255, 255), width=1)
    return im


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", help="folder with S##_rgb.png and S##_ir.png")
    ap.add_argument("--out", default="ir_pairs")
    ap.add_argument("--gamma", type=float, default=2.2, help="gamma for the brightened RGB panel")
    args = ap.parse_args()

    pairs = []
    for rgb in sorted(glob.glob(os.path.join(args.folder, "S*_rgb.png"))):
        ir = rgb.replace("_rgb.png", "_ir.png")
        if os.path.exists(ir):
            pairs.append((os.path.basename(rgb)[:-8], rgb, ir))
    if not pairs:
        sys.exit(f"Không thấy cặp S##_rgb.png / S##_ir.png trong {args.folder}")
    os.makedirs(args.out, exist_ok=True)
    rows = []
    for scene, rgb_p, ir_p in pairs:
        rgb, ir = Image.open(rgb_p), Image.open(ir_p)
        if rgb.size != ir.size:
            print(f"{scene}: kích thước khác nhau {rgb.size} vs {ir.size}, bỏ qua")
            continue
        for kind, im in (("rgb", rgb), ("ir", ir)):
            g = to_gray(im)
            w = g.shape[1]
            for part, sl in (("all", slice(0, w)), ("third_left", slice(0, w // 3)),
                             ("third_mid", slice(w // 3, 2 * w // 3)), ("third_right", slice(2 * w // 3, w))):
                rows.append({"scene": scene, "image": kind, "region": part,
                             **{k: round(v, 2) for k, v in stats(g[:, sl]).items()}})
        w, h = rgb.size
        sheet = Image.new("RGB", (3 * w, h))
        sheet.paste(label(rgb.convert("RGB"), f"{scene} RGB"), (0, 0))
        sheet.paste(label(brighten(rgb, args.gamma), f"RGB gamma {args.gamma}"), (w, 0))
        sheet.paste(label(ir.convert("RGB"), f"{scene} IR-sim"), (2 * w, 0))
        sheet.save(os.path.join(args.out, f"{scene}_pair.png"))
    with open(os.path.join(args.out, "ir_pairs.csv"), "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    print(f"{len(pairs)} cặp ảnh -> {args.out}/ (ảnh ghép + ir_pairs.csv)")
    print("scene  RGB mean/%dark   IR mean/%dark   gợi ý")
    for scene, *_ in pairs:
        r = next(x for x in rows if x["scene"] == scene and x["image"] == "rgb" and x["region"] == "all")
        i = next(x for x in rows if x["scene"] == scene and x["image"] == "ir" and x["region"] == "all")
        hint = "RGB tối: IR-sim giữ thêm chi tiết?" if r["pct_dark"] > 30 and i["pct_dark"] < r["pct_dark"] else ""
        print(f"{scene}   {r['mean']:6.1f}/{r['pct_dark']:5.1f}%   {i['mean']:6.1f}/{i['pct_dark']:5.1f}%   {hint}")
    print("Hãy tự nhìn ảnh ghép rồi ghi vào ir_log: scene, thuộc tính, thấy ở RGB?, thấy ở IR-sim?, vì sao.")


if __name__ == "__main__":
    main()
