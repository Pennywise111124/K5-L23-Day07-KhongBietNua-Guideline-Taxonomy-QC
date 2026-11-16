# Guideline gán nhãn — v0.1 — Đỗ Huyền

- Phiên bản: v0.1 (bản cá nhân, đề xuất để họp)
- Ngày: 2026-11-16
- Người viết / duyệt: Đỗ Huyền / chưa duyệt
- Phạm vi: 40 ảnh `data/images/img_001.jpg`–`img_040.jpg`; phát hiện vật thể 2D trong ảnh đường phố.

## 1. Mục tiêu

Nhãn dùng để huấn luyện bộ phát hiện người và phương tiện nhìn thấy trong ảnh đường phố. Bỏ sót người đi bộ/đi xe máy và phương tiện thật có thể làm mô hình không phát hiện được người hoặc xe; vì vậy gán từng đối tượng nhận diện được, kể cả khi bị che một phần. Không suy diễn phần khuất và không biến hình ảnh trang trí, phản chiếu hay vật mô phỏng thành vật thể thật.

## 2. Lớp và thuộc tính

### Lớp

| Lớp | Định nghĩa (một câu) | Ví dụ | Phản ví dụ / dễ nhầm với |
|---|---|---|---|
| `car` | Ô tô chở người, gồm sedan, hatchback, wagon, SUV và xe con ba bánh nếu rõ hình dạng ô tô. | Ô tô đỗ trên phố. | Xe tải; mô hình hoặc tượng ô tô. |
| `truck` | Xe cơ giới chở hàng cỡ lớn, gồm cabin và thùng/khung chở hàng gắn liền. | Xe tải thùng; xe đầu kéo kéo rơ-moóc. | Van kín cỡ nhỏ; xe chở ô tô vẫn chỉ là truck, còn ô tô thật trên sàn là các car riêng. |
| `van` | Xe chở người/hàng cỡ nhỏ có thân kín dạng hộp, nhỏ hơn xe tải. | Van chở khách. | Pickup có thùng hở; xe tải lớn. |
| `motorcycle` | Xe hai bánh có động cơ, kể cả xe tay ga; gắn sidecar vẫn tính một xe máy nếu xe chính rõ ràng. | Xe máy chạy trên phố. | Xe đạp; tuk-tuk/xe ba bánh không có xe máy hai bánh nhận diện riêng. |
| `person` | Một người thật, kể cả người lái/khách ngồi trên xe, nếu có thể xác định được một cá thể. | Người đi bộ, người lái xe máy. | Người in trên poster, tượng người, hình vẽ. |
| `ignore_region` | Một vùng đông đặc hoặc chồng lấn đến mức không thể tách đáng tin cậy các đối tượng thuộc lớp mục tiêu. | Một cụm xe máy xa, dính liền không phân biệt được từng xe. | Một xe đơn lẻ bị che nhưng vẫn nhận dạng được. |

Vật ngoài sáu lớp trên không gán nhãn. Không tạo lớp mới. Chỉ dùng `ignore_region` cho cụm vật thuộc phạm vi nhưng không thể tách; không dùng cho tượng, hình in, phản chiếu hoặc vật không thuộc taxonomy. Tuk-tuk/xe ba bánh độc lập không có lớp phù hợp: bỏ qua và ghi `can_review` cấp ảnh nếu đó là ca cần quyết định taxonomy.

### Thuộc tính

| Thuộc tính | Mức cố định | Ngưỡng và cách chọn |
|---|---|---|
| `occluded_level` | `0`, `1`, `2`, `3` | Đếm phần diện tích hộp bao toàn vật bị vật khác che (không tính phần ngoài khung hình). `0`: 0%; `1`: >0% đến 25%; `2`: >25% đến 50%; `3`: >50% nhưng còn đủ dấu hiệu nhận diện để đặt box. Nếu không xác định chắc vật là gì hoặc không thể khoanh vùng box, không gán box và ghi vấn đề cấp ảnh để reviewer quyết định. |
| `truncated` | `no`, `yes` | `yes` khi vật thật bị mép ảnh cắt mất ít nhất một phần; nếu không thì `no`. Vật bị xe/người khác che không phải truncated. |
| `can_review` | tick / không tick | Tick nếu đối tượng đã có box nhưng lớp hoặc mức thuộc tính còn nghi vấn; thêm ghi chú ảnh/vùng để nêu đúng câu hỏi. Nếu chưa biết có nên tạo box hay không, ghi vấn đề cấp ảnh thay vì tick một box giả định. |

## 3. Quy tắc vẽ box

**R-01 — Một vật thật, một box riêng.** Box chữ nhật song song trục ảnh, sát biên ngoài của phần nhìn thấy thuộc về vật; không bao khoảng trống lớn, bóng, bóng phản chiếu, hàng hóa rời hoặc người/vật khác. Mỗi người và mỗi xe là đối tượng riêng, kể cả người đang lái xe máy.

**R-02 — Người đi xe máy.** Vẽ một box `motorcycle` ôm phần nhìn thấy của xe (thân, bánh, tay lái/gương thuộc xe); vẽ thêm một box `person` cho từng người có thể phân biệt. Box người ôm phần nhìn thấy từ đầu/mũ bảo hiểm đến bàn chân/giày, gồm quần áo và cơ thể, không gồm xe. Mũ bảo hiểm đội trên đầu là một phần biên trên của box người. Hành khách sau người lái có box riêng nếu đầu và thân hoặc dấu hiệu cơ thể đủ để nhận ra cá thể; không gộp hai người vào một box. Phần bị che bởi người/xe khác không được nội suy.

Áp dụng thử cùng quy tắc cho hai ảnh: ở `img_005`, mỗi người lái/khách phân biệt được có box `person` riêng và mỗi xe máy có box `motorcycle` riêng dù người che xe; ở `img_023`, người đạp xích lô là `person`, xích lô không thuộc lớp xe đã định nghĩa, còn ô tô có box `car`. Không gộp người và phương tiện thành một box.

**R-03 — Xe chở xe.** Box xe tải chở ô tô là `truck`; mỗi ô tô thật nhìn thấy trên giá có box `car` riêng nếu nhận ra được phần thân xe. Không vẽ box cho giá đỡ/rơ-moóc như phương tiện riêng trừ khi đó là một xe kéo độc lập nhận diện rõ và có taxonomy phù hợp. Box xe tải không bao các ô tô được chở. Ví dụ: `img_002` — truck cộng các car nhìn thấy.

**R-04 — Che khuất và cắt khung.** Box chỉ ôm phần nhìn thấy, không đoán phần bị che hoặc nằm ngoài khung. Vẫn gán khi thấy dấu hiệu đủ nhận diện; ghi `occluded_level` theo tỷ lệ che ước lượng của toàn vật và `truncated=yes` nếu chạm mép ảnh làm mất vật. Nếu hai vật cùng lớp chạm nhau, tách box theo từng cá thể khi còn xác định được ranh giới; nếu không tách đáng tin cậy ở một cụm, vẽ một `ignore_region` bao cụm đó, không gộp thành box xe/người thông thường.

**R-05 — Ngưỡng kích thước.** Chỉ gán đối tượng có phần nhìn thấy ít nhất 10×10 pixel và nhận diện được lớp bằng hình dạng, không dựa riêng vào màu/chấm sáng. Dưới ngưỡng này bỏ qua theo quy tắc, không tạo box; ghi ảnh trong nhật ký ca khó nếu đối tượng là điểm cần giải thích. Áp dụng ngưỡng theo kích thước ảnh gốc, không phóng to để biến vật nhỏ thành đối tượng đủ chuẩn.

**R-06 — Vật không phải đối tượng thật trong cảnh.** Không gán người/xe trên poster, biển quảng cáo, tranh tường, màn hình, đồ chơi, xe diễu hành giả, tượng hoặc hình trong gương/kính/vũng nước. Gán đối tượng thật đứng cạnh các vật đó bình thường. `img_015`: người trên billboard không phải `person`; `img_014`: người và ngựa tượng không gán; `img_018`: xe/người phản chiếu trong gương bỏ qua. Nếu không phân biệt được ảnh phản chiếu với vật thật, cấp ảnh `can_review`.

**R-07 — Phương tiện lạ.** Nếu một xe có vẻ là phương tiện thật nhưng không khớp định nghĩa lớp (ví dụ tuk-tuk ở `img_004` hoặc xích lô ở `img_023`), không ép vào lớp gần nhất và không dùng `ignore_region` chỉ vì thiếu lớp; ghi `can_review` cấp ảnh để nhóm chốt phạm vi taxonomy. Sidecar gắn cố định vào xe máy thuộc cùng một đối tượng `motorcycle` (một box) nếu xe hai bánh chính nhận diện rõ.

## 4. Ca khó

| Ảnh | Tình huống | Rule ID | Quyết định | Lý do |
|---|---|---|---|---|
| `img_002` | Xe tải chở nhiều ô tô trên giá | R-03 | Loại xe giá đỡ; gán một `truck` và từng `car` thật nhìn thấy, mỗi xe một box; không tick reviewer nếu nhận dạng rõ. | Xe chở không làm mất tư cách là đối tượng của từng ô tô; box truck không ôm hàng chở. |
| `img_004` | Tuk-tuk ba bánh có động cơ | R-07 | Không gán vào `motorcycle` hoặc `car`; ghi `can_review` cấp ảnh để hỏi có mở rộng taxonomy không. | Không phải xe hai bánh và không phải ô tô con theo định nghĩa hiện tại. |
| `img_005` | Nhiều người đi xe máy chồng lấn/che nhau | R-01, R-02, R-04 | Gán riêng từng `person` nhận diện được và từng xe máy nhận diện được; box phần thấy được, đặt mức che theo %; tick review cho cá thể không chắc ranh giới/số người. | Người và xe là hai đối tượng khác nhau; không nội suy vùng khuất. |
| `img_007` | Dòng xe máy đông, người nhỏ ở xa | R-04, R-05 | Tách các xe/người đạt 10×10 px và có cá thể nhận ra; vùng chồng đặc không thể tách thì một `ignore_region`; bỏ qua các chấm dưới ngưỡng. | Không thể tạo box cá thể ổn định cho đám đông quá dày hoặc vật quá nhỏ. |
| `img_014` | Tượng người cưỡi ngựa | R-06 | Không gán `person`; ngựa cũng ngoài taxonomy; không box hoặc ignore. | Đây là tượng, không phải người/phương tiện thật đang tham gia giao thông. |
| `img_015` | Người trên billboard cạnh bãi xe | R-06 | Không gán người trong hình in; gán xe thật dưới đất nếu đủ ngưỡng. | Hình in không phải người trong cảnh 3D. |
| `img_018` | Xe và cảnh đường phản chiếu trong gương chiếu hậu | R-06 | Không gán các xe/người trong phần phản chiếu; chỉ gán vật thật ngoài gương nếu có. | Phản chiếu không phải đối tượng độc lập trong cảnh. |
| `img_020` | Cụm đông người và xe máy | R-04, R-05 | Tách cá thể đủ rõ; vùng không thể phân ranh dùng `ignore_region`; điểm quá nhỏ bỏ qua. Tick review nếu không biết cụm nào thuộc ignore. | Giảm box tùy tiện cho những vật không thể phân biệt. |
| `img_021` | Xe máy có sidecar | R-07 | Một box `motorcycle` ôm xe máy và sidecar gắn liền; mỗi người có box `person` riêng. | Sidecar là cấu hình của xe máy, không phải đối tượng riêng thuộc taxonomy. |
| `img_023` | Người trên xích lô giữa phố | R-01, R-07 | Gán `person`; bỏ qua xe xích lô và ghi `can_review` cấp ảnh về taxonomy. | Xích lô không thuộc lớp xe hiện có; người vẫn thuộc lớp. |
| `img_026` | Tượng xe tải trong nghĩa trang | R-06 | Không gán `car` dù hình giống xe tải. | Xe là tượng/đồ trang trí, không phải phương tiện thật. |
| `img_027` | Người chở thanh dài bằng xe máy/xe đạp | R-01, R-04 | Gán từng người và xe máy thật theo phần nhìn thấy; không đưa thanh dài vào box xe/người. Xe đạp bỏ qua. | Vật mang theo không thuộc phần thân xe; không nhầm xe đạp với motorcycle. |
| `img_028` | Bãi nhiều xe máy đậu sát nhau | R-04 | Mỗi xe có thể tách được có một box; vùng xe chồng dính không tách được gán một `ignore_region`, không gán một box `motorcycle` cho cả bãi. | Box lớp thông thường phải ứng với một phương tiện. |
| `img_017` | Xe diễu hành hình ô tô và chuột hoạt hình | R-06 | Không gán xe như `car`, người bên trong chỉ gán nếu thấy người thật rõ; hình chuột không gán. | Xe mô phỏng/diễu hành không phải ô tô giao thông thật. |

**Loại theo quy tắc:** tượng, hình in, phản chiếu, đồ chơi/xe mô phỏng, xe đạp và vật dưới ngưỡng 10×10 px được bỏ qua theo R-05/R-06/R-07; không cần reviewer nếu bản chất rõ. **Cần hỏi reviewer:** phương tiện thật nhưng taxonomy chưa có lớp (tuk-tuk, xích lô), không chắc số người/ranh giới trong vùng che dày, hoặc không chắc đó là phản chiếu hay vật thật. Ghi `can_review` trên box chỉ khi box đã được tạo; nếu câu hỏi là có tạo box hay không, ghi cấp ảnh.

## 5. QC và phiên bản

Trước khi nộp, kiểm lại đủ 40 ảnh; mỗi box là một đối tượng, lớp/thuộc tính nằm trong tập giá trị cố định, box không bao phần khuất, vật khác hoặc vùng rỗng đáng kể. Reviewer xem toàn bộ box có `can_review`, các `ignore_region`, và mọi ảnh có ghi vấn đề cấp ảnh. Ca mơ hồ được người review của nhóm chốt trước khi khóa guideline; quyết định phải cập nhật phiên bản và nếu đổi cách gán thì rà lại tất cả ảnh có cùng tình huống. Ngưỡng kích thước và mức che ở bản này là đề xuất cá nhân, cần nhóm thống nhất với taxonomy và script trước khi dùng gán nhãn.

| Phiên bản | Thay đổi | Lý do (ca nào) |
|---|---|---|
| v0.1 | Viết lại quy tắc box, thuộc tính và ca biên; bổ sung ví dụ ảnh. | Các mơ hồ của v0 về người đi xe máy, vật bị che, xe chở xe và vật ngoài phạm vi. |
