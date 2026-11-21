#!/usr/bin/env python3
"""Check a CVAT "CVAT for images 1.1" export against Guideline Cabin v1.0.

  python3 cabin_check.py check annotations.xml [--expect 24-28] [--manifest manifest.csv] [--json out.json]
  python3 cabin_check.py diff mine.xml peer.xml [--iou 0.5] [--csv disagreement_log.csv]

`check` runs the self-check (E2). `diff` compares two learners' exports of the same images for
peer review (E3) without a shared server. Agreement between two learners shows consistency, not
correctness. The coach's GT or the guideline decides who is right.

Exit code: 0 = no errors (warnings allowed), 1 = errors found, 2 = file could not be read.
Fallback if the script cannot run: the manual checklist in the lab (section "Tự kiểm").
"""
import argparse
import csv
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cabin_schema import (FACE13_POINTS, LABELS, MIN_FACE13_WIDTH_PX, SEATED_LABELS,  # noqa: E402
                          TWO_REAR_SEAT_CARS)


# ---------- parsing ----------

def load_xml(path):
    """Accept the .xml itself or the .zip CVAT exports (annotations.xml inside)."""
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            names = [n for n in z.namelist() if n.endswith(".xml")]
            if not names:
                raise ValueError(f"{path}: zip has no .xml file")
            return ET.fromstring(z.read(names[0]))
    return ET.parse(path).getroot()


def _attrs(el):
    return {a.get("name"): (a.text or "").strip() for a in el.findall("attribute")}


def parse_images(root):
    images = []
    for img in root.findall("image"):
        rec = {"name": os.path.basename(img.get("name", "")), "width": float(img.get("width", 0) or 0),
               "height": float(img.get("height", 0) or 0), "boxes": [], "tags": [], "skeletons": [], "other": []}
        for el in img:
            if el.tag == "box":
                rec["boxes"].append({"label": el.get("label"), "attrs": _attrs(el),
                                     "xyxy": tuple(float(el.get(k)) for k in ("xtl", "ytl", "xbr", "ybr")),
                                     "occluded": el.get("occluded") == "1"})
            elif el.tag == "tag":
                rec["tags"].append({"label": el.get("label"), "attrs": _attrs(el)})
            elif el.tag == "skeleton":
                pts = []
                for p in el.findall("points"):
                    xy = (p.get("points") or "").split(",")
                    pts.append({"label": p.get("label"), "occluded": p.get("occluded"), "outside": p.get("outside"),
                                "xy": (float(xy[0]), float(xy[1])) if len(xy) == 2 and xy[0] else None})
                rec["skeletons"].append({"label": el.get("label"), "points": pts})
            else:
                rec["other"].append({"tag": el.tag, "label": el.get("label")})
        images.append(rec)
    return images


def car_of(image_name, manifest):
    """Car model from the manifest (fetch_sviro_subset.py) or from a SVIRO-style file name."""
    stem = os.path.splitext(image_name)[0]
    if stem in manifest:
        return manifest[stem]
    m = re.match(r"(?:s\d+_)?([a-z0-9]+?)_(?:train|test)_", image_name.lower())
    return m.group(1) if m else None


def load_manifest(path):
    out = {}
    if path:
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                for col in ("ir_file", "rgb_file"):
                    if row.get(col):
                        out[os.path.splitext(os.path.basename(row[col]))[0]] = row["car"].lower()
    return out


# ---------- check ----------

def check_attrs(where, label, attrs, issues):
    spec = LABELS[label][1]
    for a, allowed in spec.items():
        v = attrs.get(a)
        if v is None or v == "":
            issues.append(("ERROR", where, f"{label}: thiếu thuộc tính '{a}'"))
        elif v not in allowed:
            issues.append(("ERROR", where, f"{label}: {a}='{v}' không hợp lệ (cho phép: {', '.join(allowed)})"))
    for a in attrs:
        if a not in spec:
            issues.append(("WARN", where, f"{label}: thuộc tính lạ '{a}' (không có trong guideline)"))


def inside(pt, box, pad=0.15):
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    return x1 - pad * w <= pt[0] <= x2 + pad * w and y1 - pad * h <= pt[1] <= y2 + pad * h


def check_image(img, manifest):
    issues, n = [], img["name"]
    # frame_meta: exactly one per image
    metas = [t for t in img["tags"] if t["label"] == "frame_meta"]
    if len(metas) != 1:
        issues.append(("ERROR", n, f"cần đúng 1 tag frame_meta, đang có {len(metas)}"))
    for t in img["tags"]:
        if t["label"] not in LABELS or LABELS[t["label"]][0] != "tag":
            issues.append(("ERROR", n, f"tag '{t['label']}' không có trong guideline"))
        else:
            check_attrs(n, t["label"], t["attrs"], issues)
    for o in img["other"]:
        issues.append(("ERROR", n, f"kiểu hình '{o['tag']}' ({o['label']}) không dùng trong guideline"))

    car = car_of(n, manifest)
    # SVIRO scenes are S##_ir.png / S##_rgb.png (fetch_sviro_subset.py) or keep the SVIRO file name
    is_sviro = car is not None or re.match(r"S\d+_(ir|rgb)\.png$", n, re.I) is not None
    if is_sviro and metas and metas[0]["attrs"].get("light") not in (None, "unknown"):
        issues.append(("WARN", n, "ảnh SVIRO là ảnh dựng: light nên là 'unknown'"))

    seats_used = {}
    faces = []
    for b in img["boxes"]:
        lab = b["label"]
        if lab not in LABELS or LABELS[lab][0] != "rectangle":
            issues.append(("ERROR", n, f"box label '{lab}' không có trong guideline (hoặc sai kiểu)"))
            continue
        x1, y1, x2, y2 = b["xyxy"]
        if x2 - x1 < 2 or y2 - y1 < 2:
            issues.append(("ERROR", n, f"{lab}: box suy biến ({x2 - x1:.0f}x{y2 - y1:.0f} px)"))
        check_attrs(n, lab, b["attrs"], issues)
        if lab in SEATED_LABELS:
            seat = b["attrs"].get("seat")
            if seat == "rear_middle" and car in TWO_REAR_SEAT_CARS:
                issues.append(("ERROR", n, f"{lab}: xe {car} chỉ có 2 ghế sau, không có rear_middle"))
            if is_sviro and seat in ("driver", "front_passenger"):
                issues.append(("WARN", n, f"{lab}: seat={seat} trên ảnh SVIRO (camera chỉ nhìn hàng ghế sau)"))
            seats_used.setdefault(seat, []).append(lab)
        if lab == "person" and is_sviro and b["attrs"].get("seatbelt") in ("worn_correct", "worn_incorrect"):
            issues.append(("WARN", n, "SVIRO không gắn dây an toàn (trang data SVIRO): kiểm lại seatbelt"))
        if lab == "face":
            faces.append(b)
    for seat, labs in seats_used.items():
        main = [l for l in labs if l in ("person", "child_seat", "infant_seat")]
        if main.count("person") > 1 or main.count("child_seat") > 1 or main.count("infant_seat") > 1:
            issues.append(("WARN", n, f"ghế {seat} có nhiều box cùng loại: {labs}"))
        if "child_seat" in main and "infant_seat" in main:
            issues.append(("WARN", n, f"ghế {seat} có cả child_seat và infant_seat"))

    # face13 skeletons
    for s in img["skeletons"]:
        if s["label"] != "face13":
            issues.append(("ERROR", n, f"skeleton '{s['label']}' không có trong guideline"))
            continue
        names = [p["label"] for p in s["points"]]
        missing = [p for p in FACE13_POINTS if p not in names]
        extra = [p for p in names if p not in FACE13_POINTS]
        if missing or extra or len(names) != 13:
            issues.append(("ERROR", n, f"face13 phải có đúng 13 điểm; thiếu {missing}, thừa {extra}"))
        for p in s["points"]:
            if p["occluded"] not in ("0", "1") or p["outside"] not in ("0", "1"):
                issues.append(("ERROR", n, f"face13.{p['label']}: thiếu cờ occluded/outside"))
        vis = {p["label"]: p["xy"] for p in s["points"] if p["outside"] == "0" and p["xy"]}
        if len(vis) == 0:
            issues.append(("WARN", n, "face13 không có điểm nào hiện: nếu không thấy mặt thì đừng vẽ face13"))
        # left/right by the person: in a frontal face the person's left eye is on image right.
        le, re_ = vis.get("left_eye_outer"), vis.get("right_eye_outer")
        if le and re_ and le[0] < re_[0]:
            issues.append(("WARN", n, "left_eye_outer nằm bên trái ảnh so với right_eye_outer: "
                                      "kiểm lại quy ước trái/phải theo người (đúng nếu mặt quay hẳn sang bên)"))
        host = [f for f in faces if vis and sum(inside(xy, f["xyxy"]) for xy in vis.values()) >= len(vis) / 2]
        if not host:
            issues.append(("WARN", n, "face13 không nằm trong box face nào"))
        for f in host:
            w = f["xyxy"][2] - f["xyxy"][0]
            if w < MIN_FACE13_WIDTH_PX:
                issues.append(("ERROR", n, f"face13 trên mặt rộng {w:.0f} px (< {MIN_FACE13_WIDTH_PX} px không gán face13)"))
        if len(host) == 1:
            issues += check_eye_flags(n, host[0]["attrs"], s["points"])

    # hand.side is the person's own left/right: one person has at most one left and one right hand
    sides = {}
    for b in img["boxes"]:
        if b["label"] == "hand" and b["attrs"].get("side") in ("left", "right"):
            k = (b["attrs"].get("whose"), b["attrs"]["side"])
            sides[k] = sides.get(k, 0) + 1
    for (whose, side), cnt in sorted(sides.items()):
        if cnt > 1:
            issues.append(("ERROR", n, f"hand: {cnt} tay whose={whose} cùng side={side}. side là trái/phải của chính "
                                       "người đó (không theo phía ảnh): mỗi người chỉ có 1 tay trái, 1 tay phải"))
    return issues


def check_eye_flags(n, face_attrs, points):
    """eye_<side> must agree with the occluded/outside flags of that eye's 4 face13 points."""
    out = []
    for side in ("left", "right"):
        state = face_attrs.get(f"eye_{side}")
        pts = [p for p in points if p["label"].startswith(f"{side}_eye_")]
        if not pts:
            continue
        hidden = [p for p in pts if p["occluded"] == "1" or p["outside"] == "1"]
        if state == "unknown" and not hidden:
            out.append(("WARN", n, f"eye_{side}=unknown nhưng không điểm {side}_eye_* nào có cờ occluded/outside: "
                                   "nếu mắt bị che thì bật occluded, nếu thấy rõ thì chọn open/closed"))
        elif state in ("open", "closed") and len(hidden) == len(pts):
            out.append(("WARN", n, f"eye_{side}={state} nhưng cả {len(pts)} điểm {side}_eye_* đều bị che: "
                                   "không thấy mắt thì eye_{side} nên là unknown".replace("{side}", side)))
    return out


def parse_expect(s):
    if not s:
        return None
    a, _, b = s.partition("-")
    return int(a), int(b or a)


def cmd_check(args):
    try:
        images = parse_images(load_xml(args.xml))
    except (ET.ParseError, ValueError, OSError) as e:
        print(f"Không đọc được file: {e}")
        return 2
    manifest = load_manifest(args.manifest)
    issues = []
    rng = parse_expect(args.expect)
    if rng and not (rng[0] <= len(images) <= rng[1]):
        issues.append(("ERROR", "(task)", f"có {len(images)} ảnh, cần {rng[0]}–{rng[1]}"))
    counts = {}
    for img in images:
        issues += check_image(img, manifest)
        for b in img["boxes"]:
            counts[b["label"]] = counts.get(b["label"], 0) + 1
        for s in img["skeletons"]:
            counts[s["label"]] = counts.get(s["label"], 0) + 1
    done = sum(1 for img in images if any(t["label"] == "frame_meta" for t in img["tags"]))
    err = sum(1 for i in issues if i[0] == "ERROR")
    warn = len(issues) - err
    print(f"File: {args.xml}")
    print(f"Ảnh: {len(images)} · đã có frame_meta: {done} · số đối tượng: "
          + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    for lvl, where, msg in sorted(issues, key=lambda i: (i[1], i[0])):
        print(f"  [{lvl}] {where}: {msg}")
    print(f"Kết quả: {err} lỗi, {warn} cảnh báo. Cảnh báo cần bạn tự xét, không tự động là sai.")
    if args.json:
        with open(args.json, "w") as f:
            json.dump({"images": len(images), "with_frame_meta": done, "counts": counts,
                       "issues": [dict(level=l, image=w, message=m) for l, w, m in issues]},
                      f, ensure_ascii=False, indent=2)
    return 1 if err else 0


# ---------- diff (peer review) ----------

def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def cmd_diff(args):
    try:
        mine = {i["name"]: i for i in parse_images(load_xml(args.mine))}
        peer = {i["name"]: i for i in parse_images(load_xml(args.peer))}
    except (ET.ParseError, ValueError, OSError) as e:
        print(f"Không đọc được file: {e}")
        return 2
    rows = []
    common = sorted(set(mine) & set(peer))
    for name in sorted(set(mine) ^ set(peer)):
        rows.append([name, "-", "image", "chỉ có ở " + ("mine" if name in mine else "peer"), "", ""])
    for name in common:
        a, b = mine[name], peer[name]
        ta = {k: v for t in a["tags"] if t["label"] == "frame_meta" for k, v in t["attrs"].items()}
        tb = {k: v for t in b["tags"] if t["label"] == "frame_meta" for k, v in t["attrs"].items()}
        for k in sorted(set(ta) | set(tb)):
            if ta.get(k) != tb.get(k):
                rows.append([name, "frame_meta", k, "khác giá trị", ta.get(k, ""), tb.get(k, "")])
        used = set()
        for ba in a["boxes"]:
            best, bi = 0.0, None
            for j, bb in enumerate(b["boxes"]):
                if j in used or bb["label"] != ba["label"]:
                    continue
                v = iou(ba["xyxy"], bb["xyxy"])
                if v > best:
                    best, bi = v, j
            if bi is None or best < args.iou:
                rows.append([name, ba["label"], "box", "chỉ có ở mine (hoặc IoU thấp)", f"IoU={best:.2f}", ""])
                continue
            used.add(bi)
            bb = b["boxes"][bi]
            for k in sorted(set(ba["attrs"]) | set(bb["attrs"])):
                if ba["attrs"].get(k) != bb["attrs"].get(k):
                    rows.append([name, ba["label"], k, f"khác giá trị (IoU={best:.2f})",
                                 ba["attrs"].get(k, ""), bb["attrs"].get(k, "")])
        for j, bb in enumerate(b["boxes"]):
            if j not in used:
                rows.append([name, bb["label"], "box", "chỉ có ở peer (hoặc IoU thấp)", "", ""])
        if len(a["skeletons"]) != len(b["skeletons"]):
            rows.append([name, "face13", "count", "khác số skeleton", len(a["skeletons"]), len(b["skeletons"])])
        for sa, sb in zip(a["skeletons"], b["skeletons"]):
            pa = {p["label"]: p for p in sa["points"]}
            pb = {p["label"]: p for p in sb["points"]}
            for p in FACE13_POINTS:
                for flag in ("occluded", "outside"):
                    if p in pa and p in pb and pa[p][flag] != pb[p][flag]:
                        rows.append([name, "face13", f"{p}.{flag}", "khác cờ", pa[p][flag], pb[p][flag]])
    header = ["image", "label", "field", "issue", "mine", "peer"]
    print(f"So sánh {len(common)} ảnh chung · {len(rows)} điểm khác. Mỗi dòng cần ghi: ai đúng theo guideline, "
          "luật nào, hay đây là ca mơ hồ cần hỏi.")
    for r in rows:
        print("  " + " | ".join(str(x) for x in r))
    if args.csv:
        with open(args.csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(header + ["verdict", "guideline_rule", "action"])
            w.writerows(r + ["", "", ""] for r in rows)
        print(f"Đã ghi {args.csv} (cột verdict/guideline_rule/action để bạn điền).")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="tự kiểm một file export")
    c.add_argument("xml")
    c.add_argument("--expect", help="số ảnh mong đợi, ví dụ 24-28")
    c.add_argument("--manifest", help="manifest.csv từ fetch_sviro_subset.py (để biết xe nào)")
    c.add_argument("--json", help="ghi kết quả JSON")
    d = sub.add_parser("diff", help="so sánh với file của bạn review chéo")
    d.add_argument("mine")
    d.add_argument("peer")
    d.add_argument("--iou", type=float, default=0.5)
    d.add_argument("--csv", help="ghi disagreement_log.csv")
    args = ap.parse_args()
    sys.exit(cmd_check(args) if args.cmd == "check" else cmd_diff(args))


if __name__ == "__main__":
    main()
