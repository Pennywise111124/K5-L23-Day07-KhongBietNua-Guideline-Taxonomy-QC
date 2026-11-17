"""Gộp nhiều file COCO export từ CVAT (mỗi file một phần ảnh) thành một file.

Dùng:  python pha5/merge_coco.py <file_ra.json> <vào1.json> <vào2.json> ...
- Mỗi ảnh chỉ được xuất hiện trong ĐÚNG MỘT file vào (trùng ảnh -> báo lỗi).
- Danh sách lớp (tên và id) của các file phải giống nhau.
- ID ảnh và annotation được đánh số lại; ảnh sắp theo tên file.
"""
import json, sys

def main():
    if len(sys.argv) < 3:
        print(__doc__); return 1
    out, ins = sys.argv[1], sys.argv[2:]
    data = [json.load(open(p, encoding="utf-8")) for p in ins]
    cats = [(c["id"], c["name"]) for c in data[0]["categories"]]
    for p, d in zip(ins, data):
        if [(c["id"], c["name"]) for c in d["categories"]] != cats:
            print(f"LỖI: {p} có danh sách lớp khác file đầu tiên."); return 1
    seen, items = {}, []
    for p, d in zip(ins, data):
        imgs = {i["id"]: i for i in d["images"]}
        by_img = {}
        for a in d["annotations"]:
            by_img.setdefault(a["image_id"], []).append(a)
        for i in d["images"]:
            fn = i["file_name"]
            if fn in seen:
                print(f"LỖI: ảnh {fn} có trong cả {seen[fn]} và {p}."); return 1
            seen[fn] = p
            items.append((fn, i, by_img.get(i["id"], [])))
    items.sort(key=lambda t: t[0])
    images, anns, aid = [], [], 1
    for new_id, (fn, i, al) in enumerate(items, 1):
        ni = dict(i); ni["id"] = new_id; images.append(ni)
        for a in al:
            na = dict(a); na["id"] = aid; na["image_id"] = new_id; anns.append(na); aid += 1
    res = dict(data[0]); res["images"], res["annotations"] = images, anns
    json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Đã gộp {len(images)} ảnh, {len(anns)} annotation -> {out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
