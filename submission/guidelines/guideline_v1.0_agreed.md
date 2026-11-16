# Guideline gán nhãn — v1.0 agreed

- Phiên bản: v1.0
- Ngày chốt: 2026-11-16
- Phạm vi: 40 ảnh đường phố `img_001.jpg`–`img_040.jpg`
- Loại nhãn: bounding box, xuất COCO 1.0 từ CVAT
- Taxonomy tương ứng: `submission/taxonomy.json` phiên bản `v1.0`

## 1. Mục tiêu và nguyên tắc chung

Gán người thật và phương tiện đường bộ thật có trong ảnh. Mỗi đối tượng được nhận diện và đủ ngưỡng kích thước có một box riêng, thuộc đúng một lớp. Mức che, cắt mép và yêu cầu xem lại là thuộc tính, không phải lớp.

Không gán hình in, hình vẽ, tượng, ma-nơ-canh, mascot, đồ chơi, vật trưng bày hoặc phản chiếu như người hay phương tiện thật. Không gán vật ngoài taxonomy. `ignore_region` chỉ đánh dấu vùng có người/phương tiện thuộc taxonomy nhưng không thể tách hoặc định vị đáng tin cậy; không dùng để gom vật ngoài phạm vi.

## 2. Lớp

| Lớp | Định nghĩa và ranh giới |
|---|---|
| `person` | Người thật, gồm người đi bộ, người lái và hành khách trên phương tiện; mỗi người là một box. Người trong cabin chỉ gán khi phần nhìn thấy đủ nhận ra là người. |
| `motorcycle` | Xe máy, mô tô, xe tay ga hai bánh có động cơ. Sidecar gắn cố định tính cùng một xe máy và nằm trong box xe. |
| `car` | Ô tô chở người thân liền khối, gồm sedan, hatchback, wagon, SUV, taxi và ô tô cá nhân khác. Không gồm pickup hoặc xe chở khách thân dài. |
| `van` | Xe kín cỡ nhỏ/vừa, cabin và khoang xe liền khối, như Hiace hoặc van giao hàng. |
| `truck` | Xe có cabin và khoang hàng tách nhau: xe tải, đầu kéo, bán tải/pickup (kể cả gắn canopy hoặc bạt), xe ben và xe chở ô tô. |
| `bus` | Xe buýt, xe khách hoặc minibus có thân chở khách dài/dãy cửa sổ hành khách; xe buýt nhìn từ sau vẫn là `bus`. Minivan kiểu Hiace là `van`. |
| `three_wheeler` | Phương tiện ba bánh chở người/hàng, gồm tuk-tuk, auto-rickshaw và xích lô đạp. Không gồm xe máy hai bánh gắn sidecar. |
| `ignore_region` | Vùng bỏ qua chứa nhiều người hoặc phương tiện thuộc các lớp trên nhưng không tách được từng đối tượng. Đây là vùng, không phải một vật thể. |

### Thứ tự phân lớp phương tiện

Áp dụng lần lượt, dừng khi tìm được lớp phù hợp:

1. Vật không thật hoặc phản chiếu: không gán.
2. Phương tiện ba bánh không phải xe máy có sidecar: `three_wheeler`.
3. Xe máy hai bánh có động cơ, kể cả sidecar: `motorcycle`.
4. Xe chở khách thân dài/có dãy cửa sổ hành khách: `bus`.
5. Cabin tách khoang hàng: `truck`.
6. Thân kín liền cabin cỡ nhỏ/vừa: `van`.
7. Ô tô chở người còn lại: `car`.

Xe đạp, xích lô hai bánh, xe đẩy, thuyền, hàng hóa, động vật và vật không phải người/phương tiện trong taxonomy không được gán box lớp. Người đạp/đẩy vẫn được gán `person` nếu đủ điều kiện. Không dùng `ignore_region` cho các vật này.

## 3. Thuộc tính

Các thuộc tính và giá trị phải khớp `submission/taxonomy.json`. Gán thuộc tính cho box đối tượng; để mặc định trên `ignore_region`.

| Thuộc tính | Quy tắc |
|---|---|
| `occluded_level` | Ước lượng phần trăm diện tích vật bị vật khác che, không tính phần nằm ngoài khung ảnh. `0`: dưới 10%; `1`: từ 10% đến dưới 40%; `2`: từ 40% đến dưới 70%; `3`: từ 70% trở lên nhưng vẫn nhận ra chắc chắn lớp. Nếu không nhận ra chắc chắn thì không tạo box lớp. |
| `truncated` | `yes` khi vật thật tiếp tục ra ngoài bất kỳ mép ảnh nào; box chỉ nằm trong ảnh. Cắt mép không được tính là che khuất. Nếu vừa bị che vừa cắt mép, điền cả hai thuộc tính. |
| `can_review` | Tick cho box đã tạo khi còn nghi vấn thực sự về lớp, ranh giới box hoặc thuộc tính. Nếu chưa chắc có vật/box hay không, không tạo box phỏng đoán; ghi ảnh, vùng và lý do vào nhật ký vấn đề cấp ảnh. |

## 4. Quy tắc vẽ box

**R-01 — Một đối tượng, một box.** Box hình chữ nhật song song cạnh ảnh, ôm sát phần nhìn thấy. Không gộp nhiều người/xe; không gồm bóng, khoảng nền lớn, hàng hóa rời hoặc phần khuất được suy đoán.

**R-02 — Người và phương tiện tách riêng.** Với người đi xe máy hoặc tuk-tuk, tạo box phương tiện và một box `person` cho từng người nhận diện được, kể cả người ngồi sau. Box có thể chồng nhau tại phần tiếp xúc; box người không bao xe và box xe không bao người. Người trong cabin được gán nếu thấy đủ rõ.

**R-03 — Che khuất.** Vẽ phần nhìn thấy, không nội suy phần bị vật khác che. Chỉ gán đối tượng bị che nếu vẫn nhận ra chắc chắn lớp; ghi `occluded_level` theo mục 3. Không dùng mức che thay cho việc quyết định lớp.

**R-04 — Cắt mép.** Box dừng đúng mép ảnh. Gán vật nếu phần trong ảnh đủ nhận dạng và chiều cao box nhìn thấy đạt ngưỡng. Đặt `truncated=yes` khi vật bị khung ảnh cắt, bất kể phần mất ước lượng bao nhiêu.

**R-05 — Ngưỡng kích thước.** Box lớp thường chỉ tạo khi chiều cao phần nhìn thấy đạt `min_box_height_px = 20` trong ảnh gốc. Vật thuộc taxonomy thấp hơn ngưỡng không vẽ box riêng; nếu tạo thành cụm mục tiêu dày/không tách được thì có thể đánh dấu cụm bằng `ignore_region`. Không tạo vùng ignore chỉ để bao một vật đơn lẻ dưới ngưỡng.

**R-06 — Đám đông và cụm phương tiện.** Tách box riêng cho từng đối tượng thuộc taxonomy còn nhận diện được, đủ ngưỡng và có ranh giới đáng tin cậy. Dùng một `ignore_region` cho phần cụm mục tiêu quá dày, quá nhỏ hoặc mờ đến mức không thể tách từng vật. Không gộp cụm vào box `person`/phương tiện thường.

**R-07 — Xe chở xe và hàng hóa.** Box `truck` bao đầu kéo/cabin và khung xe chở, không bao ô tô được chở hoặc hàng nhô khỏi thân xe. Mỗi ô tô thật trên xe chở được nhận diện và đạt ngưỡng có box `car` riêng. Hàng hóa (bao tải, ống, cuộn dây, thùng hàng) không có box và không làm box phương tiện phình ra.

**R-08 — Xe giả, vật trưng bày và xe chủ.** Không gán tượng, mô hình, đồ chơi, xe trưng bày, hình in/vẽ, mascot hoặc phản chiếu trong gương/kính/mặt nước. Xe thật đang đỗ vẫn được gán. Không gán phần thân/gương của xe đang chụp ảnh (ego vehicle). Xe diễu hành có khả năng tự chạy và đang được lái được gán theo loại xe; mascot/hình trang trí trên xe không gán.

**R-09 — Mờ và không chắc chắn.** Vật mờ nhưng vẫn nhận ra chắc chắn lớp và đạt ngưỡng thì gán, ôm phần nhìn thấy và tick `can_review` nếu ranh giới/lớp còn nghi vấn. Vệt mờ không nhận diện được từng vật không có box lớp; dùng `ignore_region` chỉ khi đó là cụm mục tiêu.

## 5. Quyết định tham chiếu cho các ca trong bộ ảnh

Các dòng dưới đây minh họa cách áp dụng quy tắc; mọi ảnh khác áp dụng cùng quy tắc chung.

| Ảnh | Quyết định thống nhất |
|---|---|
| `img_002` | Một `truck` cho đầu kéo và khung; từng ô tô được chở đủ rõ/đủ ngưỡng là `car` riêng. |
| `img_004`, `img_016`, `img_035`, `img_040` | Tuk-tuk/auto-rickshaw là `three_wheeler`; người lái nhìn rõ là `person` riêng. Hàng chở không thuộc box xe. |
| `img_005`, `img_006`, `img_026` | Mỗi xe máy là `motorcycle`; mỗi người trên xe là `person` riêng nếu nhận diện được. |
| `img_009` | Minibus có dãy cửa sổ khách là `bus`; người trong xe chỉ gán khi nhìn thấy đủ rõ để nhận ra là người. |
| `img_017`, `img_027`, `img_033`, `img_038` | Tượng, xe tượng, ma-nơ-canh và đồ chơi không được gán; không tạo `ignore_region` chỉ vì chúng hiện diện. |
| `img_019` | Xe diễu hành có khả năng chạy và đang được lái là `car`; tài xế là `person`; mascot không gán. Người trong đám đông tách được thì box riêng, phần không tách được có thể là `ignore_region`. |
| `img_020` | Không gán xe chủ hoặc cảnh trong gương chiếu hậu. |
| `img_022`, `img_025` | Xe máy có sidecar là một `motorcycle`, box gồm sidecar; người lái là `person` nếu đủ ngưỡng và nhận diện được. |
| `img_023` | Xích lô đạp là `three_wheeler`; người đạp là `person`; xe đạp và vật ngoài taxonomy không gán. |
| `img_024` | Gán các ô tô thật nhìn thấy, kể cả xe thật đang được chở trên nóc; không gán vật trang trí/mô hình nếu xác định là mô hình. |
| `img_031`, `img_037`, `img_040` | Xe buýt là `bus`, kể cả nhìn từ sau/xa nếu còn nhận diện được và đạt ngưỡng. Pickup có nắp thùng/canopy vẫn là `truck`. |

## 6. QC và quản lý phiên bản

Áp dụng nguyên trạng các ngưỡng trong `submission/taxonomy.json` → `rules`: `min_box_height_px`, IoU box lớn/nhỏ, ngưỡng IAA, ngưỡng ghép và tỷ lệ lỗi ảnh. Không thay đổi các số đó trong guideline này.

QC cần xác nhận: lớp thuộc taxonomy; mỗi box ứng với một đối tượng; box ôm phần nhìn thấy; người và xe tách riêng; thuộc tính hợp lệ; `ignore_region` chỉ phủ vùng mục tiêu không tách được. Ảnh không có đối tượng thuộc phạm vi vẫn phải có trong COCO với 0 box.

Khi gặp ca chưa được quy định hoặc người gán bất đồng, ghi mã ảnh, vùng, lựa chọn đang phân vân và lý do. Nhóm chốt thành quyết định có mã quy tắc trong phiên bản tiếp theo; không tự thay quy tắc v1.0 giữa lượt gán độc lập.

| Phiên bản | Thay đổi |
|---|---|
| v0 | Taxonomy khởi đầu: `car`, `truck`, `van`, `motorcycle`, `person`, `ignore_region`. |
| v1.0 | Chốt định nghĩa `bus`, `three_wheeler`; làm rõ ranh giới xe tải/van/bus, người trên xe, xe chở xe, vật ngoài phạm vi, box phần nhìn thấy, che khuất, cắt mép, vật nhỏ và QC. |
