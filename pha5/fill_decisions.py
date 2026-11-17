"""Điền submission/qc/calibration_decisions.csv theo nhóm, KHÔNG điền khống kết quả.

Chạy từ thư mục gốc repo. Thứ tự bắt buộc (do script của bài đòi):

  1) decide : điền quyet_dinh, quy_tac, phien_ban, nguoi_chot, pham_vi theo decisions_config.json
        python pha5/fill_decisions.py decide --config pha5/decisions_config.json [--dry-run]
  2) pending: điền phieu_sua/kiem_lai bằng KẾ HOẠCH (ghi rõ "chưa thực hiện": ai sửa, ai kiểm)
        python pha5/fill_decisions.py pending [--dry-run]
     -> cần bước này vì prepare_calibration.py đòi mọi cột đã có chữ TRƯỚC khi sửa nhãn.
  3) (chạy scripts/prepare_calibration.py, sửa nhãn trong CVAT, người khác kiểm lại)
  4) fixlog : thay kế hoạch bằng KẾT QUẢ THẬT từ fix_log.csv
        python pha5/fill_decisions.py fixlog --fixlog fix_log.csv [--dry-run]
     fix_log.csv: image,nguoi_sua,phieu_sua,nguoi_kiem,ket_qua_kiem (mỗi ảnh một dòng, người điền tay)
  5) check  : báo lỗi nếu còn dòng "KẾ HOẠCH (chưa thực hiện)"
        python pha5/fill_decisions.py check

Sau bước 4 nội dung bảng đổi nên mã băm đổi: chạy lại scripts/prepare_calibration.py, lấy đường dẫn
labels_calibrated_<hash>.json MỚI và đặt file nhãn đã gộp vào đúng đường dẫn đó, rồi chạy build_final.py.
"""
import argparse, csv, json, math, sys
from pathlib import Path

QC = Path("submission/qc")
COLS = ["case_id", "image", "quyet_dinh", "quy_tac_ghi_vao_guideline", "phien_ban_guideline",
        "nguoi_chot", "phieu_sua", "kiem_lai", "pham_vi"]
PENDING = "KẾ HOẠCH (chưa thực hiện)"

def read(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def write(p, rows):
    with open(p, "w", encoding="utf-8", newline="") as f:   # không BOM, giống repo
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

def members():
    return sorted(p.stem for p in (QC / "assignments").glob("*.txt"))

def die(msg):
    print("LỖI:", msg); sys.exit(1)

def decide(cfg_path, dry, overwrite):
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    chot = cfg.get("nguoi_chot", "")
    if chot not in members():
        die(f"nguoi_chot '{chot}' không phải mã thành viên trong assignments ({members()}).")
    cands = {r["case_id"]: r for r in read(QC / "calibration_candidates.csv")}
    rows = read(QC / "calibration_decisions.csv")
    overrides = {k: v for k, v in cfg.get("overrides", {}).items() if not k.startswith("_")}
    unresolved, changed, by_rule = [], 0, {}
    for r in rows:
        cid = r["case_id"]
        if (r.get("quyet_dinh") or "").strip() and not overwrite:
            continue
        c = cands.get(cid)
        if c is None:
            unresolved.append(cid); continue
        if cid in overrides:
            o = overrides[cid]
            rule, text, scope = o["rule"], o["quyet_dinh"], o.get("pham_vi", cfg["pham_vi_mac_dinh"])
        else:
            hits = [x for x in cfg["rules"] if x["issue_type"] == c["issue_type"]
                    and ("match_note" not in x or x["match_note"] in (c.get("ghi_chu_tu_dong") or ""))]
            if not hits:
                unresolved.append(cid); continue
            rule = ", ".join(dict.fromkeys(x["rule"] for x in hits))
            text = " | ".join(x["quyet_dinh"] for x in hits)
            scope = cfg["pham_vi_mac_dinh"]
        if scope not in {"anh", "lo"}:
            die(f"{cid}: pham_vi phải là anh hoặc lo.")
        r.update(quyet_dinh=text, quy_tac_ghi_vao_guideline=rule,
                 phien_ban_guideline=cfg["phien_ban_guideline"], nguoi_chot=chot, pham_vi=scope)
        changed += 1
        by_rule[rule] = by_rule.get(rule, 0) + 1
    if unresolved:
        die("Còn ca chưa có quy tắc hoặc override (cần quyết định tay): " + ", ".join(unresolved[:40])
            + (f" ... (+{len(unresolved)-40})" if len(unresolved) > 40 else ""))
    print(f"Sẽ điền {changed} dòng. Theo quy tắc: {by_rule}")
    if dry:
        print("(dry-run: chưa ghi file)"); return
    write(QC / "calibration_decisions.csv", rows)
    print("Đã ghi calibration_decisions.csv. Bước tiếp: python pha5/fill_decisions.py pending")

def plan_owner(rows):
    """Chia đều ảnh theo thứ tự tên cho các thành viên; người kiểm là người kế tiếp."""
    mem = members()
    imgs_dir = Path("data/images")
    imgs = sorted(p.name for p in imgs_dir.glob("*.jpg")) if imgs_dir.is_dir() else sorted({r["image"] for r in rows})
    block = math.ceil(len(imgs) / len(mem))
    def who(img):
        k = imgs.index(img) // block
        return mem[k], mem[(k + 1) % len(mem)]
    return who

def pending(dry, overwrite):
    rows = read(QC / "calibration_decisions.csv")
    who = plan_owner(rows)
    n = 0
    for r in rows:
        if not (r.get("quyet_dinh") or "").strip():
            die(f"{r['case_id']}: chưa có quyet_dinh. Chạy bước decide trước.")
        sua, kiem = who(r["image"])
        if overwrite or not (r.get("phieu_sua") or "").strip():
            r["phieu_sua"] = f"{PENDING}: {sua} sửa ảnh này trong CVAT theo v1.1"; n += 1
        if overwrite or not (r.get("kiem_lai") or "").strip():
            r["kiem_lai"] = f"{PENDING}: {kiem} kiểm lại sau khi sửa"
    print(f"Sẽ điền kế hoạch cho {n} dòng (chưa phải kết quả thật).")
    if dry:
        print("(dry-run: chưa ghi file)"); return
    write(QC / "calibration_decisions.csv", rows)
    print("Đã ghi. Bước tiếp: python scripts/prepare_calibration.py (nhớ bỏ dòng BẢN NHÁP khỏi guideline trước).")

def fixlog(path, dry):
    mem = set(members())
    log = {r["image"]: r for r in read(path)}
    rows = read(QC / "calibration_decisions.csv")
    bad = []
    for img in sorted({r["image"] for r in rows}):
        l = log.get(img)
        if not l or not all((l.get(k) or "").strip() for k in ("nguoi_sua", "phieu_sua", "nguoi_kiem", "ket_qua_kiem")):
            bad.append(f"{img}: thiếu dòng hoặc thiếu trường trong fix_log.csv"); continue
        if l["nguoi_sua"] not in mem or l["nguoi_kiem"] not in mem:
            bad.append(f"{img}: nguoi_sua/nguoi_kiem phải là mã thành viên {sorted(mem)}")
        elif l["nguoi_sua"] == l["nguoi_kiem"]:
            bad.append(f"{img}: người kiểm lại không được trùng người sửa")
    if bad:
        die("fix_log.csv chưa đạt:\n  " + "\n  ".join(bad))
    for r in rows:
        l = log[r["image"]]
        r["phieu_sua"] = f"{l['nguoi_sua']}: {l['phieu_sua']}"
        r["kiem_lai"] = f"{l['nguoi_kiem']}: {l['ket_qua_kiem']}"
    print(f"Sẽ thay kế hoạch bằng kết quả thật cho {len(rows)} dòng từ {len(log)} ảnh.")
    if dry:
        print("(dry-run: chưa ghi file)"); return
    write(QC / "calibration_decisions.csv", rows)
    print("Đã ghi. Bảng đã đổi nên mã băm đổi: chạy lại scripts/prepare_calibration.py để lấy đường dẫn labels_calibrated_<hash>.json mới.")

def check():
    rows = read(QC / "calibration_decisions.csv")
    left = [r["case_id"] for r in rows if PENDING in (r.get("phieu_sua") or "") or PENDING in (r.get("kiem_lai") or "")]
    if left:
        die(f"Còn {len(left)} dòng đang là KẾ HOẠCH, chưa có kết quả thật (ví dụ {left[:5]}). Điền fix_log.csv rồi chạy bước fixlog.")
    print(f"Đạt: {len(rows)} dòng đều là kết quả thật, không còn kế hoạch.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("decide"); a.add_argument("--config", required=True)
    a.add_argument("--dry-run", action="store_true"); a.add_argument("--overwrite", action="store_true")
    p = sp.add_parser("pending"); p.add_argument("--dry-run", action="store_true"); p.add_argument("--overwrite", action="store_true")
    b = sp.add_parser("fixlog"); b.add_argument("--fixlog", required=True); b.add_argument("--dry-run", action="store_true")
    sp.add_parser("check")
    x = ap.parse_args()
    if not (QC / "calibration_decisions.csv").exists() or not (QC / "calibration_candidates.csv").exists():
        die("Chạy từ thư mục gốc repo và chạy build_final.py một lần trước để tạo calibration_decisions.csv.")
    if x.cmd == "decide": decide(x.config, x.dry_run, x.overwrite)
    elif x.cmd == "pending": pending(x.dry_run, x.overwrite)
    elif x.cmd == "fixlog": fixlog(x.fixlog, x.dry_run)
    else: check()
