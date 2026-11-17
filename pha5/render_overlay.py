"""Vẽ box từ file COCO lên ảnh để người kiểm lại xem nhanh, không cần mở CVAT.

Dùng (từ thư mục gốc repo):
    python pha5/render_overlay.py <coco.json> <thư_mục_ra> [img_001.jpg img_002.jpg ...]
Không nêu ảnh thì vẽ tất cả. Nhãn hiển thị: lớp, occluded_level, truncated (T), can_review (R).
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw

COL = {"car": (230, 25, 75), "truck": (60, 180, 75), "van": (67, 99, 216), "bus": (245, 130, 49),
       "bicycle": (145, 30, 180), "motorcycle": (70, 200, 200), "three_wheeler": (240, 50, 230),
       "person": (255, 225, 25), "ignore_region": (160, 160, 160)}

def main():
    if len(sys.argv) < 3:
        print(__doc__); return 1
    coco = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[3:])
    cats = {c["id"]: c["name"] for c in coco["categories"]}
    by = {}
    for a in coco["annotations"]:
        by.setdefault(a["image_id"], []).append(a)
    n = 0
    for im in coco["images"]:
        name = Path(im["file_name"]).name
        if only and name not in only: continue
        p = Path("data/images") / name
        if not p.exists():
            print("Thiếu ảnh", p); continue
        img = Image.open(p).convert("RGB"); d = ImageDraw.Draw(img, "RGBA")
        for a in by.get(im["id"], []):
            c = cats[a["category_id"]]; col = COL.get(c, (255, 255, 255))
            x, y, w, h = a["bbox"]
            if c == "ignore_region":
                d.rectangle([x, y, x + w, y + h], fill=col + (60,), outline=col + (255,), width=2); tag = "ignore"
            else:
                at = a.get("attributes", {})
                d.rectangle([x, y, x + w, y + h], outline=col + (255,), width=3)
                tag = f"{c[:6]} o{at.get('occluded_level','?')}" + ("T" if str(at.get("truncated")).lower() == "yes" else "") \
                      + ("R" if str(at.get("can_review")).lower() == "true" else "")
            d.rectangle([x, y, x + len(tag) * 6 + 4, y + 12], fill=(0, 0, 0, 170))
            d.text((x + 2, y + 1), tag, fill=col + (255,))
        img.save(out / (Path(name).stem + ".png")); n += 1
    print(f"Đã vẽ {n} ảnh vào {out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
