"""Kiểm thuộc tính truncated theo R-16 (box chạm mép ảnh <= 2 px thì yes, ngược lại no).

Dùng:  python check_truncated_edge.py submission/labels/070.json
       python check_truncated_edge.py nhan.json --fix nhan_fixed.json   (ghi bản đã sửa, vẫn phải xem lại bằng mắt)
Không đụng tới ignore_region.
"""
import argparse, json, sys

EDGE = 2.0

def touches(a, w, h):
    x, y, bw, bh = a["bbox"]
    return x <= EDGE or y <= EDGE or x + bw >= w - EDGE or y + bh >= h - EDGE

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("coco")
    ap.add_argument("--fix")
    args = ap.parse_args()
    d = json.load(open(args.coco, encoding="utf-8"))
    cats = {c["id"]: c["name"] for c in d["categories"]}
    imgs = {i["id"]: i for i in d["images"]}
    a_no, b_yes = [], []
    for a in d["annotations"]:
        if cats[a["category_id"]] == "ignore_region":
            continue
        im = imgs[a["image_id"]]
        t = touches(a, im["width"], im["height"])
        cur = str(a.get("attributes", {}).get("truncated", "no")).lower()
        if t and cur != "yes":
            a_no.append((im["file_name"], a["id"], cats[a["category_id"]], a["bbox"]))
        if (not t) and cur == "yes":
            b_yes.append((im["file_name"], a["id"], cats[a["category_id"]], a["bbox"]))
        if args.fix:
            a.setdefault("attributes", {})["truncated"] = "yes" if t else "no"
    print(f"Chạm mép nhưng truncated=no : {len(a_no)}")
    for r in a_no: print("  ", *r)
    print(f"truncated=yes nhưng không chạm mép: {len(b_yes)}")
    for r in b_yes: print("  ", *r)
    if args.fix:
        json.dump(d, open(args.fix, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("Đã ghi", args.fix, "- xem lại các ca trước khi dùng.")
    return 0 if not (a_no or b_yes) else 1

if __name__ == "__main__":
    sys.exit(main())
