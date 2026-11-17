"""Xử lý phần máy móc của calibration trên nhãn nháp, trước khi nạp vào CVAT.

Dùng (từ thư mục gốc repo):
    python pha5/prep_consensus.py [vào.json] [ra.json]
Mặc định: work/calib/consensus_flagged.json -> work/calib/consensus_prepped.json

Việc script LÀM (theo quy tắc đã chốt, không cần nhìn ảnh):
  - R-17: đặt can_review=false cho mọi box.
  - R-16: truncated=yes khi box chạm mép ảnh (<= 2 px), ngược lại no.
  - Bảo đảm có đủ occluded_level/truncated (mặc định 0/no nếu thiếu).
Việc script CHỈ GỢI Ý (người phải xem ảnh rồi tự sửa trong CVAT):
  - R-13: cụm >= 5 box sát nhau; trong cụm, box cao < 40 px hoặc occluded_level >= 2 nên chuyển vào ignore_region.
  - R-05: box cao < 20 px (không được có box riêng).
Không tự xóa box nào.
"""
import json, sys
from collections import defaultdict
from pathlib import Path

EDGE, GAP, CLUSTER_MIN, H_MIN, H_BIG = 2.0, 6.0, 5, 40.0, 20.0

def touches(b, w, h):
    x, y, bw, bh = b
    return x <= EDGE or y <= EDGE or x + bw >= w - EDGE or y + bh >= h - EDGE

def near(a, b):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    return not (ax + aw + GAP < bx or bx + bw + GAP < ax or ay + ah + GAP < by or by + bh + GAP < ay)

def components(items):
    n = len(items); parent = list(range(n))
    def f(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            if near(items[i]["bbox"], items[j]["bbox"]):
                parent[f(i)] = f(j)
    g = defaultdict(list)
    for i in range(n): g[f(i)].append(items[i])
    return list(g.values())

def main():
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "work/calib/consensus_flagged.json")
    dst = Path(sys.argv[2] if len(sys.argv) > 2 else "work/calib/consensus_prepped.json")
    d = json.loads(src.read_text(encoding="utf-8"))
    cats = {c["id"]: c["name"] for c in d["categories"]}
    imgs = {i["id"]: i for i in d["images"]}
    n_cr = n_tr = 0
    per_img = defaultdict(list)
    for a in d["annotations"]:
        if cats[a["category_id"]] == "ignore_region":
            continue
        at = a.setdefault("attributes", {})
        at.setdefault("occluded_level", "0")
        if str(at.get("can_review", "false")).lower() == "true":
            n_cr += 1
        at["can_review"] = False
        im = imgs[a["image_id"]]
        want = "yes" if touches(a["bbox"], im["width"], im["height"]) else "no"
        if str(at.get("truncated", "no")).lower() != want:
            n_tr += 1
        at["truncated"] = want
        per_img[a["image_id"]].append(a)
    dst.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Đã ghi {dst}")
    print(f"- R-17: tắt can_review ở {n_cr} box")
    print(f"- R-16: đổi truncated ở {n_tr} box")
    print("\nGỢI Ý cần người xem ảnh (không tự sửa):")
    total_sug = 0
    for iid in sorted(per_img, key=lambda k: imgs[k]["file_name"]):
        items = per_img[iid]; name = imgs[iid]["file_name"]
        tiny = [a for a in items if a["bbox"][3] < H_BIG]
        lines = []
        for comp in components(items):
            if len(comp) < CLUSTER_MIN: continue
            cand = [a for a in comp if a["bbox"][3] < H_MIN or int(a["attributes"].get("occluded_level", 0)) >= 2]
            if not cand: continue
            xs = [a["bbox"][0] for a in cand]; ys = [a["bbox"][1] for a in cand]
            xe = [a["bbox"][0] + a["bbox"][2] for a in cand]; ye = [a["bbox"][1] + a["bbox"][3] for a in cand]
            lines.append(f"  cụm {len(comp)} box, {len(cand)} box nên vào ignore_region (R-13); vùng gợi ý "
                         f"x {min(xs):.0f}-{max(xe):.0f}, y {min(ys):.0f}-{max(ye):.0f}")
        if tiny:
            lines.append(f"  {len(tiny)} box cao < 20 px (R-05): id " + ", ".join(str(a['id']) for a in tiny[:10]))
        if lines:
            total_sug += 1
            print(name); print("\n".join(lines))
    print(f"\n{total_sug} ảnh có gợi ý." if total_sug else "\nKhông có gợi ý nào.")

if __name__ == "__main__":
    main()
