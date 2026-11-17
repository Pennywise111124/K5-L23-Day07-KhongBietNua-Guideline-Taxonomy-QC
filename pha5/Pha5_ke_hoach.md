# Pha 5: kế hoạch calibration cho nhóm KhongBietNua

Tài liệu này tổng hợp số liệu Pha 4, đề xuất quy tắc để họp, phân việc và thứ tự lệnh. Mọi quyết định cuối (quy tắc nào chốt, ai là `nguoi_chot`) là của nhóm; AI chỉ soạn nháp.

## 1. Số liệu Pha 4 nói gì
- IoU TB 0.846 (ngưỡng 0.85), đồng thuận lớp 98.3% (đạt), mẫu số 689 cặp. Chỉ trượt ở IoU.
- Thuộc tính lệch nhiều: `occluded_level` trùng 53.4%, `truncated` 85.9%.
- 1389 ca: `bo_sot_thua` 393 (person 180, motorcycle 122), `sai_thuoc_tinh` 372, `bat_dong_ignore` 269, `iou_thap` 252, `co_can_review` 91, `sai_lop` 12.
- Dồn vào ảnh đông: img_021 (134), img_008 (124), img_032 (110), img_039 (82), img_006 (68), img_025 (66). Riêng `bat_dong_ignore`, img_032 có 54 ca.
- Cặp có 070 lệch `occluded_level` nhiều nhất (25–37% với 034, 048, 344). **Nguyên nhân có thể nằm ở nhãn nháp AI của 070:** nháp đó ước mức che bằng mắt, không đối chiếu mốc 10/40/70 của v1.0 (guideline cá nhân cũ dùng 5/30/70), nên có thể lệch có hệ thống. Đây là ca "một người lệch": 070 ghi vào Mục 4 ghi chú cá nhân, không phải bằng chứng guideline mơ hồ.
- 344 và 354 vẽ nhiều box "chưa ghép" hơn hẳn (khoảng 38–52 mỗi cặp), khớp với giả thuyết nhóm hiểu R-06 (khi nào dùng `ignore_region`) theo hai cách.

## 2. Quy tắc đề xuất (file `guideline_v1.1_calibrated.md`)
| Mã | Nội dung | Giải quyết |
|---|---|---|
| R-13 | Cụm từ 5 vật sát nhau: chỉ vẽ riêng vật cao từ 40 px và che dưới 40%, còn lại `ignore_region` | `bo_sot_thua`, `bat_dong_ignore` |
| R-14 | Cách đo mức che (thấy 90/60/30%), lưỡng lự chọn mức cao | `sai_thuoc_tinh` (che) |
| R-15 | Cạnh box chạm điểm ngoài cùng (sai số 2 px); bộ phận cố định tính vào box, hàng và vật mang theo thì không | `iou_thap` |
| R-16 | `truncated=yes` khi box chạm mép ảnh (≤ 2 px) và vật tiếp tục ra ngoài | `sai_thuoc_tinh` (cắt mép) |
| R-17 | Giải quyết hết `can_review`; nhãn cuối không còn tick | `co_can_review` |

**Chỗ cần nhóm quyết (đừng chấp nhận nháp mà chưa bàn):**
- R-13: ngưỡng 5 vật, 40 px, 40% là đề xuất. Phương án khác: vẽ riêng mọi vật cao từ 20 px nhìn thấy từ 50% (nhiều box hơn, ít `ignore_region`).
- R-14: "lưỡng lự chọn mức cao" chỉ là cách làm cho mọi người chọn giống nhau; nhóm có thể chọn quy tắc khác nhưng phải có một.
- R-15: danh sách bộ phận cố định (gương, tay lái, yên, biển taxi, sidecar) cần nhóm xác nhận.
- 12 ca `sai_lop` cần quyết **từng ca**: `python -c "import csv; [print(r['case_id'], r['image'], r['ghi_chu_tu_dong']) for r in csv.DictReader(open('submission/qc/calibration_candidates.csv', encoding='utf-8-sig')) if r['issue_type']=='sai_lop']"`.
- `guideline_change.json` đề xuất `semantic` (đổi cách chọn vật, ranh giới, thuộc tính), nên phải kiểm lại cả 40 ảnh.

## 3. Họp (khoảng 45 phút)
1. 5': xem `work/viz/_overview.png`, img_021, img_008, img_032.
2. 15': chốt R-13 (cụm đông). Mở từng ảnh, mỗi người nói to sẽ vẽ gì, tới khi cả nhóm trả lời giống nhau.
3. 10': R-14 và R-16 (thuộc tính), thử trên 3 ảnh.
4. 5': R-15 (ranh giới box).
5. 5': 12 ca `sai_lop`.
6. 5': R-17 và quyết `nguoi_chot` cho bảng quyết định.

## 4. Phân việc (đề xuất theo mã MSSV)
| Mã | Việc |
|---|---|
| 034 | Chủ trì họp, giữ bảng quyết định (`nguoi_chot`) |
| 048 | Hoàn thiện `guideline_v1.1_calibrated.md` và `guideline_change.json` sau họp |
| 070 | Điều phối git (branch `pha5/calibration`, merge), chạy `build_final.py`, `prepare_calibration.py`; ghi Mục 4 ghi chú cá nhân |
| 344 | Chuẩn bị Task calibration trong CVAT, hướng dẫn nạp `consensus_flagged.json` |
| 354 | Kiểm lại chéo, chuẩn bị Pha 6 (`qc_sample.py`) |

Sửa nhãn trong CVAT cho 40 ảnh nên chia đều, mỗi người sửa 8 ảnh, **người kiểm lại là người khác** (script `fill_decisions.py fixlog` từ chối nếu trùng):

| Người sửa | Người kiểm lại | Ảnh |
|---|---|---|
| 034 | 048 | img_001–img_008 |
| 048 | 070 | img_009–img_016 |
| 070 | 344 | img_017–img_024 |
| 344 | 354 | img_025–img_032 |
| 354 | 034 | img_033–img_040 |

## 5. Thứ tự lệnh (từ thư mục gốc repo) — đã sửa theo cách script của bài thực sự chạy

`prepare_calibration.py` đòi mọi cột của `calibration_decisions.csv` đã có chữ **trước khi** sửa nhãn, và đường dẫn `labels_calibrated_<hash>.json` được tính từ nội dung bảng quyết định và guideline. Vì vậy `phieu_sua`/`kiem_lai` được điền hai lượt: **kế hoạch** trước, **kết quả thật** sau.

```powershell
git checkout main
git pull origin main
git checkout -b pha5/calibration
python scripts/build_final.py
```
Lần đầu sẽ báo thiếu `guideline_change.json` (bình thường): bảng `calibration_decisions.csv` đã được tạo.

**Sau họp (nhóm đã chốt quy tắc):**
```powershell
copy pha5\guideline_v1.1_calibrated.md submission\guidelines\guideline_v1.1_calibrated.md
copy pha5\guideline_change.json submission\guideline_change.json
```
Sửa guideline theo quyết định nhóm, rồi **bỏ 2 dòng đầu "BẢN NHÁP"** (phải làm trước `prepare_calibration.py`, vì guideline nằm trong mã băm):
```powershell
python -c "p='submission/guidelines/guideline_v1.1_calibrated.md'; s=open(p,encoding='utf-8').read().split('\n',2)[2]; open(p,'w',encoding='utf-8',newline='\n').write(s)"
```
Sửa `nguoi_chot` trong `pha5\decisions_config.json`, rồi:
```powershell
python pha5\fill_decisions.py decide --config pha5\decisions_config.json --dry-run
python pha5\fill_decisions.py decide --config pha5\decisions_config.json
python pha5\fill_decisions.py pending
python scripts/prepare_calibration.py
```
Lệnh cuối in `COCO sau sửa: submission\qc\labels_calibrated_<hash>.json`. Tạm ghi lại, nhưng đường dẫn này sẽ đổi ở bước điền kết quả thật.

**Sửa nhãn trong CVAT** (mỗi người 8 ảnh), export `calib_<mã>.json`, người kiểm lại xác nhận. Gộp:
```powershell
python pha5\merge_coco.py work\calib_merged.json work\calib_parts\calib_034.json work\calib_parts\calib_048.json work\calib_parts\calib_070.json work\calib_parts\calib_344.json work\calib_parts\calib_354.json
python pha5\check_truncated_edge.py work\calib_merged.json
```

**Điền kết quả thật** (`fix_log.csv`: `image,nguoi_sua,phieu_sua,nguoi_kiem,ket_qua_kiem`, mỗi ảnh một dòng, người điền tay):
```powershell
python pha5\fill_decisions.py fixlog --fixlog fix_log.csv
python pha5\fill_decisions.py check
python scripts/prepare_calibration.py
```
Lần chạy `prepare_calibration.py` này in đường dẫn **mới**. Đặt file đã gộp vào đúng đường dẫn đó, rồi gộp nhãn cuối:
```powershell
copy work\calib_merged.json submission\qc\labels_calibrated_<hash_moi>.json
python scripts/build_final.py
```

## 6. Không được tự động hóa
- Quyết định nhóm (chốt R-xx, `nguoi_chot`).
- Sửa box trong CVAT và việc người khác kiểm lại. Dòng "KẾ HOẠCH (chưa thực hiện)" chỉ là chỗ giữ chỗ để qua bước `prepare_calibration.py`; `check` chặn nếu còn sót khi nộp.
- Ghi trung thực trong ghi chú cá nhân và báo cáo QC rằng nhãn nháp ban đầu của 070 do AI soạn.
