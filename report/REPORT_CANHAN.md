# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Lê Thanh Tình
**Nhóm:** TooSweet
**Ngày:** 20/09/2026

> **Chiến lược của bản báo cáo này: `FixedSizeChunker` có chồng chéo (overlap).**
>
> Số liệu trong file được đo thật trên corpus chung `data/shopee-returns/` (10 tài liệu chính sách Trả hàng/Hoàn tiền của Shopee) và bộ 5 câu hỏi đánh giá chung của nhóm, bằng `LocalEmbedder` (`paraphrase-multilingual-MiniLM-L12-v2`). Các mục phản ngẫm cá nhân và bảng tự đánh giá để trống — người nộp tự viết.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> Bước nhảy giữa hai chunk liên tiếp là `step = chunk_size - overlap = 500 - 50 = 450`.
> Các vị trí bắt đầu là 0, 450, 900, ..., 9900 (vòng lặp dừng khi `start + 500 >= 10000`).
> Số chunk = `ceil((10000 - 500) / 450) + 1 = 22 + 1 = 23`.
> **Đáp án: 23 chunks**, chunk cuối chỉ dài 100 ký tự.

**Nếu overlap tăng lên 100?**

> `step` giảm còn 400 nên số chunk tăng lên **25**. Cả hai con số đã kiểm chứng bằng `FixedSizeChunker(chunk_size=500, overlap=ov).chunk("a" * 10000)`.

Công thức tổng quát:

```
so_chunk = ceil((L - chunk_size) / (chunk_size - overlap)) + 1     khi L > chunk_size
so_chunk = 1                                                        khi L <= chunk_size
```

Chi phí do overlap gây ra: mỗi chunk lặp lại `overlap` ký tự của chunk trước, nên tổng lượng ký tự phải embed là khoảng `L * chunk_size / (chunk_size - overlap)`. Với 500/50 là **+11%**, với 500/100 là **+25%**, với 500/200 là **+67%**. Đây là cái giá phải trả để đổi lấy việc không cắt đứt ngữ cảnh ở ranh giới.

---

## 2. Hướng tiếp cận (My Approach) — Cá nhân (10 điểm)

### Vì sao chọn FixedSizeChunker có overlap cho chủ đề này

Chiến lược này là đường cơ sở trung thực nhất: nó **không giả định gì về cấu trúc tài liệu**. Corpus của nhóm được thu thập bằng crawler, và chất lượng cấu trúc rất không đồng đều — 8/10 tài liệu chỉ có đúng một tiêu đề Markdown (dòng `# tiêu đề` do crawler sinh), phần mục của điều khoản bị đổ xuống thành dòng văn bản thường; một tài liệu (`shopee-refund-timeline`) vốn là bảng bị làm phẳng hoàn toàn. Mọi chiến lược dựa vào tiêu đề đều phụ thuộc vào việc nguồn có tiêu đề tử tế hay không, còn cắt theo độ dài thì luôn chạy được.

Overlap là phần bù cho nhược điểm cố hữu của cắt theo độ dài: ranh giới rơi vào đâu là ngẫu nhiên đối với nội dung. Một điều khoản như "Thời gian nhận được tiền hoàn: 7 - 14 ngày làm việc" hoàn toàn có thể bị cắt làm đôi, khiến không chunk nào chứa trọn vế điều kiện lẫn vế con số. Cho các chunk chồng lên nhau `overlap` ký tự thì mỗi đoạn văn bản ngắn hơn `overlap` được bảo đảm xuất hiện nguyên vẹn trong ít nhất một chunk.

### Cách hoạt động

```python
class FixedSizeChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks
```

Ba chi tiết đáng chú ý trong cách lập trình:

- **Cửa sổ trượt bằng `range(0, len(text), step)`** — bước nhảy là `step`, còn bề rộng cửa sổ là `chunk_size`, nên phần giao nhau đúng bằng `overlap`.
- **Điều kiện dừng sớm** `if start + self.chunk_size >= len(text): break` ngăn việc sinh ra các chunk đuôi trùng lặp. Không có dòng này, vòng lặp vẫn chạy tiếp và tạo thêm những chunk chỉ chứa phần cuối văn bản.
- **Lối thoát cho văn bản ngắn** `if len(text) <= self.chunk_size: return [text]` — trả về nguyên văn thay vì một danh sách một phần tử đã bị cắt.

**Rủi ro cần biết:** nếu `overlap >= chunk_size` thì `step <= 0` và `range()` sẽ ném `ValueError`. Lớp này không chặn trường hợp đó, nên người dùng phải tự bảo đảm `overlap < chunk_size`.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

### Kết Quả Kiểm Thử (Test Results)

```
$ pytest tests/ -q
..........................................                               [100%]
42 passed in 0.04s
```

**Số lượng bài test vượt qua (pass):** 42 / 42

> Kết quả trên chạy bằng gói `src` trong repo này. Mỗi sinh viên nộp kết quả `pytest` từ gói `src` của chính mình.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

> Cột "Dự đoán" phải được điền **trước** khi chạy. Bảng dưới để trống phần dự đoán; điểm thực tế đã đo sẵn bằng `LocalEmbedder`, ngưỡng phân loại cao/thấp đặt ở 0.5.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Thẻ tín dụng/ghi nợ: 7 - 14 ngày làm việc. | Tiền hoàn về thẻ tín dụng mất khoảng hai tuần làm việc. | | 0.727 | |
| 2 | Người mua có 7 ngày để gửi yêu cầu trả hàng. | Người bán phải phản hồi khiếu nại trong 2 ngày lịch. | | 0.506 | |
| 3 | Sản phẩm số và dịch vụ không được trả hàng. | Thực phẩm tươi sống không áp dụng lý do trả hàng Đổi ý. | | 0.204 | |
| 4 | Dung lượng video bằng chứng tối đa là 100 MB. | Ví ShopeePay hoàn tiền trong vòng 24 giờ. | | 0.114 | |
| 5 | Return and refund policy for buyers on Shopee. (EN) | Chính sách trả hàng và hoàn tiền dành cho người mua trên Shopee. (VI) | | 0.768 | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Cấu hình đem đi chấm: **`FixedSizeChunker(chunk_size=500, overlap=100)`** trên corpus 10 tài liệu, cho ra **99 chunk**, trung bình 480 ký tự.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được | Score | Có liên quan? | Điểm |
|---|-------|--------------------------------|-------|-----------|------|
| 1 | Sau khi Shopee chấp nhận yêu cầu THHT, người mua phải gửi trả sản phẩm trong bao lâu? | Chunk thuộc `shopee-return-conditions` | 0.857 | Có trong top-3 nhưng không ở top-1 | **1** |
| 2 | Với đơn hàng thanh toán bằng thẻ tín dụng/ghi nợ, nhận tiền hoàn trong bao lâu? | Chunk thuộc `shopee-refund-timeline` | 0.679 | Đúng tài liệu ở top-1, nhưng **không chunk nào trong top-3 chứa "7 - 14 ngày làm việc"** | **1** |
| 3 | Dung lượng video tối đa khi tải bằng chứng? | Chunk thuộc `shopee-return-evidence` | 0.790 | Có, top-1, chứa đáp án | **2** |
| 4 | Nhóm sản phẩm nào không áp dụng lý do "Đổi ý"? | Chunk thuộc `shopee-return-conditions` | 0.564 | Có trong top-3 nhưng không ở top-1 | **1** |
| 5 | Thời hạn phản hồi của người bán? (lọc `audience: seller`) | Chunk thuộc `shopee-return-policy-seller` | 0.756 | Có, top-1, chứa đáp án | **2** |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5 / 5**
**Tổng điểm theo rubric (2đ/câu):** **7 / 10**

### Quét tham số: overlap thật sự ảnh hưởng thế nào

Chạy cùng 5 câu hỏi trên 6 cấu hình khác nhau của `FixedSizeChunker`, cộng `HeadingChunker` của thành viên khác để đối chiếu:

| Chiến lược | Số chunk | Độ dài TB | Điểm rubric |
|---|---|---|---|
| HeadingChunker (chia theo tiêu đề) | 60 | 681 | 8/10 |
| Fixed 500 / overlap 0 | 82 | 471 | 7/10 |
| Fixed 500 / overlap 50 | 89 | 479 | 6/10 |
| Fixed 500 / overlap 100 | 99 | 480 | 7/10 |
| Fixed 500 / overlap 200 | 127 | 488 | 6/10 |
| **Fixed 300 / overlap 50** | **158** | **291** | **8/10** |
| Fixed 800 / overlap 100 | 59 | 739 | 7/10 |

**Kết luận bất ngờ nhất: tăng overlap không làm điểm tăng đơn điệu.** Dãy 0 → 50 → 100 → 200 cho ra 7 → 6 → 7 → 6 điểm. Với cỡ mẫu chỉ 5 câu hỏi, chênh lệch một điểm hoàn toàn nằm trong khoảng nhiễu — kết luận trung thực là **overlap trong khoảng 0–200 không tạo khác biệt đo được** ở quy mô này, chứ không phải "overlap làm hại".

**Điều thật sự tạo khác biệt là kích thước chunk, không phải overlap.** Cấu hình 300/50 đạt 8/10, ngang với chiến lược chia theo tiêu đề, trong khi 800/100 chỉ được 7/10. Chunk ngắn hơn thì vector đặc trưng hơn, ít bị pha loãng bởi nội dung không liên quan — đổi lại số chunk tăng từ 59 lên 158, tức chi phí embedding gấp gần ba lần.

### Overlap có tác dụng — nhưng rubric không nhìn thấy

Chỉ nhìn điểm rubric sẽ kết luận sai rằng overlap vô dụng. Đo thứ hạng của chunk chứa đúng đáp án câu 2 ("7 - 14 ngày làm việc") trong toàn bộ kho:

| Cấu hình | Số chunk chứa đáp án | Thứ hạng cao nhất |
|---|---|---|
| Fixed 500 / overlap 0 | 2 | 9 / 60 |
| Fixed 500 / overlap 50 | 2 | 7 / 60 |
| Fixed 500 / overlap 100 | 2 | **4 / 60** |
| Fixed 500 / overlap 200 | 3 | 5 / 60 |

Overlap kéo chunk chứa đáp án từ hạng 9 lên hạng 4 — cải thiện rõ ràng và gần như đơn điệu. Nhưng vì ngưỡng chấm là top-3, cải thiện này **không đổi được điểm nào**. Đây là bài học về đo đạc: một chỉ số nhị phân theo ngưỡng có thể che giấu hoàn toàn tiến bộ thật của hệ thống. Nếu đo bằng MRR hay Recall@5 thay vì Hit@3, overlap sẽ hiện ra là có ích.

### Điểm yếu cố hữu, thấy rõ nhất ở câu 2

Ở **mọi** cấu hình `FixedSizeChunker`, câu 2 chỉ được 1 điểm: hệ thống tìm đúng tài liệu `shopee-refund-timeline` nhưng không chunk nào trong top-3 chứa con số "7 - 14 ngày làm việc". Nguyên nhân là tài liệu này liệt kê 8 phương thức hoàn tiền liên tiếp, mỗi phương thức chỉ vài chục ký tự. Cắt theo độ dài 500 ký tự sẽ gộp 3–4 phương thức vào chung một chunk, khiến vector của chunk trở thành "trung bình" của nhiều phương thức và không chunk nào đặc trưng cho riêng thẻ tín dụng. Overlap 50–200 ký tự không cứu được vì khoảng cách giữa tên phương thức và con số tương ứng trải dài hơn thế.

Cùng câu hỏi đó, `HeadingChunker` được 2 điểm vì nó cắt đúng ranh giới từng phương thức, cho ra một chunk 171 ký tự chỉ nói về thẻ tín dụng. Đây là minh họa trực tiếp cho giới hạn của chiến lược cắt theo độ dài: nó không thể biết đâu là ranh giới ngữ nghĩa, và overlap chỉ vá được ranh giới bị cắt sai, không tạo ra được ranh giới đúng.

### Nơi chiến lược này thắng

Ở câu 1, `FixedSizeChunker` đưa được chunk chứa "6 ngày" vào top-3 (1 điểm), trong khi `HeadingChunker` trượt hoàn toàn (0 điểm) vì tiêu đề của mục chứa đáp án là "3. Phân loại phương án xử lý" — không hề nhắc tới thời hạn, nên breadcrumb kéo vector đi chệch hướng. Cắt theo độ dài không gắn tiêu đề vào chunk nên cũng không bị tiêu đề đánh lừa. Đây là đánh đổi đối xứng: chiến lược theo tiêu đề mạnh khi tiêu đề mô tả đúng nội dung, và yếu đúng lúc tiêu đề mô tả sai.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
