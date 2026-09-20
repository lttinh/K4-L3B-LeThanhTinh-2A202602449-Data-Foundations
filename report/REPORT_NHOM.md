# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** TooSweet
**Thành viên:** Phạm Long Nhật,Lê Thanh Tình,Trần Xuân Đức,Nguyễn Tiến Lượng,
**Ngày:** 20/9/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách Trả hàng/Hoàn tiền của sàn thương mại điện tử Shopee Việt Nam (nguồn: Trung tâm trợ giúp `help.shopee.vn`).

**Tại sao nhóm chọn chủ đề này?**
> Chính sách đổi trả là loại văn bản có cấu trúc điều khoản rõ ràng, nhiều con số cụ thể (thời hạn, dung lượng, phí) nên câu trả lời chuẩn kiểm chứng được tuyệt đối — không phải diễn giải cảm tính. Đây là điều kiện cần để chấm điểm truy xuất một cách khách quan.
> Chủ đề này còn có sẵn hai đối tượng đọc tách bạch là người mua và người bán, cho phép gán `audience` làm trường lọc thật sự có việc để làm, đúng yêu cầu riêng của lớp L3B.
> Cuối cùng, toàn bộ nội dung nằm ở trang trợ giúp công khai, không cần đăng nhập, nên thỏa ràng buộc quản trị dữ liệu trong `docs/DATA_COLLECTION.md`.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Chính sách trả hàng dành cho người mua | `help.shopee.vn/portal/4/article/77251` | 2026-09-20 / 2026-03-11 | 3.655 | `audience: buyer`, `category: return-policy`, `language: vi` |
| 2 | Quyền và trách nhiệm của người bán khi trả hàng | `help.shopee.vn/portal/4/article/77251` | 2026-09-20 / 2026-03-11 | 2.725 | `audience: seller`, `category: return-policy`, `language: vi` |
| 3 | Điều kiện và thời hạn trả hàng | `help.shopee.vn/portal/4/article/188931` | 2026-09-20 / not-stated | 6.203 | `audience: buyer`, `category: return-conditions`, `language: vi` |
| 4 | Hướng dẫn gửi yêu cầu trả hàng | `help.shopee.vn/portal/4/article/79233` | 2026-09-20 / not-stated | 2.367 | `audience: buyer`, `category: return-request`, `language: vi` |
| 5 | Quy trình xử lý yêu cầu trả hàng | `help.shopee.vn/portal/4/article/190242` | 2026-09-20 / not-stated | 7.982 | `audience: buyer`, `category: return-process`, `language: vi` |
| 6 | Bằng chứng khi yêu cầu trả hàng | `help.shopee.vn/portal/4/article/79467` | 2026-09-20 / not-stated | 3.331 | `audience: buyer`, `category: return-evidence`, `language: vi` |
| 7 | Phương thức và phí gửi hàng hoàn trả | `help.shopee.vn/portal/4/article/189477` | 2026-09-20 / not-stated | 5.811 | `audience: buyer`, `category: return-shipping`, `language: vi` |
| 8 | Thời gian nhận tiền hoàn | `help.shopee.vn/portal/4/article/189473` | 2026-09-20 / not-stated | 4.049 | `audience: buyer`, `category: refund-timeline`, `language: vi`, `cleaning: manual-table-restructured` |
| 9 | Sản phẩm hạn chế trả hàng | `help.shopee.vn/portal/4/article/79465` | 2026-09-20 / not-stated | 1.354 | `audience: buyer`, `category: return-restrictions`, `language: vi` |
| 10 | Phản hồi đề xuất hoàn tiền ngay | `help.shopee.vn/portal/4/article/190387` | 2026-09-20 / not-stated | 1.224 | `audience: buyer`, `category: instant-refund`, `language: vi` |

Tổng 10 tài liệu, 38.701 ký tự nội dung (không tính front matter). Kiểm kê đầy đủ ở `data/shopee-returns/sources.csv`; danh sách URL để tái lập lượt crawl ở `data/urls.csv`.

> **Ghi chú về tài liệu 1 và 2.** Trang gốc `article/77251` gộp điều khoản cho cả người mua lẫn người bán. Nhóm tách thành hai file, mỗi file một `audience`, theo đúng hướng dẫn tại `docs/DATA_COLLECTION.md` §4 — nếu để chung thì `search_with_filter()` không có gì để lọc.
>
> **Ghi chú về tài liệu 8.** Bản crawl gốc là một bảng bị công cụ trích xuất làm phẳng thành các dòng rời rạc, không còn tiêu đề nào. Nhóm làm sạch tay, tái cấu trúc thành heading cho từng phương thức hoàn tiền; đã đối chiếu lại toàn bộ mốc thời gian để chắc chắn không con số nào bị thêm, sửa hay mất. Trường `cleaning: manual-table-restructured` đánh dấu việc này.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ. Toàn bộ 10 trang đều mở công khai trên Trung tâm trợ giúp Shopee, không trang nào nằm sau đăng nhập.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata. Đã kiểm bằng script: 10/10 file đủ 6 trường bắt buộc, `doc_id` trùng tên file, `sources.csv` khớp một-một với thư mục.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | enum `buyer` / `seller` | `seller` | Trường lọc chính. Embedding gần như không phân biệt được câu của người mua với câu của người bán (nhóm đo được 0.506 giữa hai câu như vậy), nên phải lọc bằng metadata. |
| `category` | chuỗi | `refund-timeline` | Thu hẹp theo chủ đề con khi câu hỏi đã rõ loại (thời gian hoàn tiền, điều kiện, bằng chứng...), tránh chunk cùng từ khóa nhưng khác mục đích. |
| `language` | mã ISO | `vi` | Cho phép mở rộng corpus sang tiếng Anh mà không trộn lẫn; hiện cả 10 tài liệu đều `vi`. |
| `source_url` | URL | `help.shopee.vn/portal/4/article/77251` | Truy vết nguồn để agent trích dẫn và để kiểm chứng câu trả lời chuẩn. |
| `retrieved_at` | ngày `YYYY-MM-DD` | `2026-09-20` | Biết dữ liệu cũ tới mức nào; chính sách sàn thay đổi thường xuyên. |
| `document_version` | ngày hiệu lực hoặc `not-stated` | `2026-03-11` | Phân biệt phiên bản điều khoản. Dùng `not-stated` khi nguồn không nêu — không bịa số hiệu. |
| `doc_id` | chuỗi không dấu | `shopee-return-policy-seller` | Khóa để `delete_document()` xóa toàn bộ chunk của một tài liệu trong một lượt. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

Chạy `ChunkingStrategyComparator().compare(text, chunk_size=500)` trên 3 tài liệu đại diện. Cột cuối là đánh giá định tính khi đọc trực tiếp các chunk sinh ra.

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Chính sách trả hàng cho người mua (3.655 ký tự) | FixedSizeChunker (`fixed_size`) | 8 | 456 | Không — cắt giữa câu, nhiều chunk mở đầu bằng nửa vế |
| | SentenceChunker (`by_sentences`) | 11 | 330 | Một phần — câu trọn vẹn nhưng mất mục cha, không biết điều khoản nào |
| | RecursiveChunker (`recursive`) | 10 | 363 | Khá — bám ranh giới đoạn, hiếm khi cắt giữa câu |
| | **HeadingChunker (chiến lược của nhóm)** | **6** | **609** | **Tốt — trùng khít ranh giới mục, có breadcrumb tiêu đề cha** |
| Phương thức và phí gửi hàng hoàn trả (5.811 ký tự) | FixedSizeChunker (`fixed_size`) | 12 | 484 | Không |
| | SentenceChunker (`by_sentences`) | 9 | 643 | Một phần — chunk dài vì nhiều câu ghép |
| | RecursiveChunker (`recursive`) | 14 | 413 | Khá |
| | **HeadingChunker** | **10** | **581** | **Tốt — tách đúng các mục 1.1 đến 3** |
| Thời gian nhận tiền hoàn (4.049 ký tự) | FixedSizeChunker (`fixed_size`) | 9 | 449 | Không — cắt ngang bảng, một chunk lẫn nhiều phương thức |
| | SentenceChunker (`by_sentences`) | 10 | 401 | Kém — bảng đã làm phẳng nên "câu" là các dòng rời rạc |
| | RecursiveChunker (`recursive`) | 9 | 448 | Kém — cùng lý do |
| | **HeadingChunker** | **11** | **387** | **Tốt — mỗi phương thức hoàn tiền một chunk, sau khi làm sạch tay** |

**Nhận xét đường cơ sở.** Ba chiến lược có sẵn cho số chunk và độ dài khá giống nhau (8–14 chunk, 330–643 ký tự) vì cả ba đều chia theo độ dài hoặc dấu câu — tức đều mù với cấu trúc điều khoản. Khác biệt chỉ lộ ra khi đọc nội dung chunk: `fixed_size` cắt giữa câu, còn `by_sentences` và `recursive` tuy giữ câu trọn vẹn nhưng chunk không mang thông tin nó thuộc mục nào, nên khi truy xuất ra một đoạn nói "trong vòng 6 ngày" thì không biết 6 ngày cho việc gì.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Phạm Long Nhật**
- **Loại chiến lược:** custom — `HeadingChunker` (chia theo tiêu đề/mục)
- **Mô tả & lý do chọn cho chủ đề này:** Văn bản chính sách vốn đã được soạn theo điều khoản đánh số, nên ranh giới ngữ nghĩa tự nhiên nhất chính là tiêu đề mục — không phải 500 ký tự hay 3 câu. Chunker nhận cả tiêu đề Markdown (`#` đến `######`) lẫn mục đánh số (`1.`, `1.1`, `2.3.1.`), vì crawler chỉ sinh đúng một `# tiêu đề` cho mỗi trang còn mục của điều khoản bị đổ xuống thành dòng văn bản thường — nếu chỉ bắt `#` thì 8/10 tài liệu sẽ ra đúng một chunk, tức không chia nhỏ gì cả.
- **Điểm khác biệt chính:** mỗi chunk được ghép thêm chuỗi tiêu đề cha dạng `Tài liệu > Mục > Mục con`, để một chunk lẻ vẫn tự nói được nó thuộc điều khoản nào. Corpus 10 tài liệu cho ra 60 chunk, trung bình 681 ký tự.
- **Code snippet:**
```python
_ATX_HEADING = re.compile(r"^(#{1,6})\s+(\S.*)$")
_NUMBERED_HEADING = re.compile(r"^(\d+(?:\.\d+)+\.?|\d+\.)\s+(\S.*)$")


class HeadingChunker:
    def __init__(self, include_parent_headings: bool = True) -> None:
        self.include_parent_headings = include_parent_headings

    def _heading(self, line: str) -> tuple[int, str] | None:
        atx = _ATX_HEADING.match(line)
        if atx:
            return len(atx.group(1)), atx.group(2).strip()
        numbered = _NUMBERED_HEADING.match(line)
        if numbered:
            # muc danh so nam thap hon tieu de ATX cung do sau mot bac
            return numbered.group(1).rstrip(".").count(".") + 2, line.strip()
        return None

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        sections: list[tuple[int, str, list[str]]] = []
        preamble: list[str] = []
        for line in text.splitlines():
            heading = self._heading(line)
            if heading is None:
                (sections[-1][2] if sections else preamble).append(line)
            else:
                sections.append((heading[0], heading[1], []))

        chunks: list[str] = []
        if preamble and "".join(preamble).strip():
            chunks.append("\n".join(preamble).strip())

        trail: list[tuple[int, str]] = []
        for level, title, body in sections:
            trail = [item for item in trail if item[0] < level]
            trail.append((level, title))
            heading_line = " > ".join(t for _, t in trail) if self.include_parent_headings else title
            content = "\n".join(body).strip()
            chunks.append(f"{heading_line}\n\n{content}" if content else heading_line)
        return chunks
```

> **Một lỗi đã gặp và sửa, đáng nói trong demo.** Biểu thức nhận mục đánh số lúc đầu là `^(\d+(?:\.\d+)*)\.?\s+`, khớp mọi dòng mở đầu bằng số và khoảng trắng. Tài liệu "Thời gian nhận tiền hoàn" là bảng đã làm phẳng nên có nhiều dòng dạng `7 - 14 ngày làm việc (tùy theo ngân hàng)` — những dòng này bị nhận nhầm thành tiêu đề mục số 7, sinh ra 9 chunk rác. Siết lại thành `^(\d+(?:\.\d+)+\.?|\d+\.)\s+` (bắt buộc có dấu chấm hoặc nhiều cấp) thì hết.

**Thành viên 2 — Lê Thanh Tình**
- **Loại chiến lược:** `FixedSizeChunker` có chồng chéo (overlap) — cấu hình đem chấm: `chunk_size=500, overlap=100`
- **Mô tả & lý do chọn:** Đây là đường cơ sở không giả định gì về cấu trúc tài liệu, nên luôn chạy được kể cả với 8/10 tài liệu mà crawler chỉ sinh đúng một tiêu đề Markdown. Overlap là phần bù cho nhược điểm cố hữu của việc cắt theo độ dài — ranh giới rơi vào đâu là ngẫu nhiên đối với nội dung — bằng cách bảo đảm mọi đoạn ngắn hơn `overlap` xuất hiện nguyên vẹn trong ít nhất một chunk.
- **Kết quả:** 99 chunk, trung bình 480 ký tự, **7/10** điểm (điểm từng câu: 1, 1, 2, 1, 2).
- **Code snippet:** dùng `FixedSizeChunker` có sẵn trong `src/chunking.py`, không sửa đổi.

> **Phát hiện quan trọng nhất: overlap không làm điểm tăng đơn điệu.** Quét tham số trên cùng 5 câu hỏi cho dãy overlap 0 → 50 → 100 → 200 ra điểm 7 → 6 → 7 → 6. Với cỡ mẫu 5 câu, chênh lệch một điểm nằm trong khoảng nhiễu, nên kết luận trung thực là overlap trong khoảng 0–200 **không tạo khác biệt đo được** ở quy mô này — chứ không phải overlap có hại.
>
> **Nhưng overlap có tác dụng thật, chỉ là rubric không nhìn thấy.** Đo thứ hạng của chunk chứa đáp án câu 2 ("7 - 14 ngày làm việc") trong toàn kho: overlap 0 → hạng 9/60, overlap 50 → hạng 7/60, overlap 100 → hạng 4/60, overlap 200 → hạng 5/60. Overlap kéo chunk đúng từ hạng 9 lên hạng 4, cải thiện rõ và gần như đơn điệu, nhưng vì ngưỡng chấm là top-3 nên không đổi được điểm nào. Bài học: một chỉ số nhị phân theo ngưỡng (Hit@3) có thể che giấu hoàn toàn tiến bộ thật của hệ thống; đo bằng MRR hay Recall@5 thì overlap sẽ hiện ra là có ích.
>
> **Thứ thật sự quyết định là kích thước chunk, không phải overlap.** Cấu hình 300/50 đạt 8/10 trong khi 800/100 chỉ 7/10. Chunk ngắn hơn cho vector đặc trưng hơn, đổi lại số chunk tăng từ 59 lên 158 — chi phí embedding gấp gần ba lần.

**Thành viên 3 — Trần Xuân Đức**
- **Loại chiến lược:** `RecursiveChunker` — cấu hình đem chấm: `chunk_size=800`, separator mặc định `["\n\n", "\n", ". ", " ", ""]`
- **Mô tả & lý do chọn:** Chiến lược này đứng giữa hai thái cực: nó tôn trọng ranh giới ngữ nghĩa như chia theo tiêu đề, nhưng không phụ thuộc vào việc nguồn có tiêu đề tử tế hay không. Thuật toán ưu tiên cắt ở ranh giới lớn nhất còn khả thi (đoạn văn), chỉ khi đoạn vẫn quá dài mới hạ xuống mức nhỏ hơn (dòng, câu, từ) — nên với văn bản chính sách vốn đã chia đoạn rõ ràng, phần lớn chunk trùng khít một đoạn điều khoản trọn vẹn.
- **Kết quả:** 58 chunk, trung bình 665 ký tự, **9/10** điểm (điểm từng câu: 1, 2, 2, 2, 2) — **cao nhất nhóm**.
- **Code snippet:** dùng `RecursiveChunker` có sẵn trong `src/chunking.py`, không sửa đổi.

> **Quét tham số cho thấy một đánh đổi không hiển nhiên.** `chunk_size=300` cho 173 chunk và 8/10; `chunk_size=500` cho 94 chunk và 8/10; `chunk_size=800` cho 58 chunk và 9/10. Ở đây chunk **lớn hơn** lại tốt hơn, ngược với xu hướng quan sát được ở `FixedSizeChunker`. Lý do: vì thuật toán cắt theo ranh giới ngữ nghĩa, chunk lớn hơn nghĩa là giữ trọn cả một mục điều khoản thay vì xé nó ra; còn cắt cứng theo độ dài thì chunk lớn chỉ đơn thuần trộn thêm nội dung không liên quan.
>
> **Cấu hình 500 là cấu hình duy nhất trong toàn bộ nhóm lấy trọn 2 điểm ở câu 1** (điểm từng câu: 2, 1, 2, 1, 2) — câu mà `HeadingChunker` và `SentenceChunker` đều trượt sạch. Nó đổi 2 điểm ở câu 1 lấy 1 điểm ở câu 4, nên tổng vẫn là 8/10. Chi tiết này cho thấy xếp hạng theo tổng điểm che mất việc các cấu hình mạnh ở những câu khác nhau.

**Thành viên 4 — Nguyễn Tiến Lượng**
- **Loại chiến lược:** `SentenceChunker` — cấu hình đem chấm: `max_sentences_per_chunk=5`
- **Mô tả & lý do chọn:** Câu là đơn vị ngữ nghĩa nhỏ nhất còn tự đứng vững được, nên cắt theo câu bảo đảm không bao giờ có chunk bắt đầu hoặc kết thúc giữa chừng một mệnh đề — điều mà cắt theo độ dài không tránh được. Với văn bản chính sách, mỗi điều kiện thường gói gọn trong một tới hai câu, nên nhóm 5 câu một chunk giữ được cả điều kiện lẫn ngoại lệ đi kèm.
- **Kết quả:** 50 chunk, trung bình 769 ký tự, **8/10** điểm (điểm từng câu: 0, 2, 2, 2, 2).
- **Code snippet:** dùng `SentenceChunker` có sẵn trong `src/chunking.py`, không sửa đổi.

> **Quét tham số cho thấy số câu mỗi chunk ảnh hưởng mạnh.** `max=2` cho 117 chunk và 7/10; `max=3` cho 79 chunk và 7/10; `max=5` cho 50 chunk và 8/10. Chunk gom nhiều câu hơn thắng ở câu 2, vì tài liệu "Thời gian nhận tiền hoàn" liệt kê 8 phương thức hoàn tiền liên tiếp — gom 5 câu mới đủ chứa trọn cả tên phương thức lẫn con số tương ứng.
>
> **Điểm yếu lộ rõ ở câu 1: mọi cấu hình đều được 0 điểm.** Chunk chứa đáp án "6 ngày" không lọt top-3 ở bất kỳ giá trị `max` nào. Nguyên nhân: chiến lược này giữ câu trọn vẹn nhưng **không mang theo thông tin chunk thuộc mục nào**, nên một đoạn nói "trong vòng 6 ngày" không có gì gắn nó với khái niệm "sau khi Shopee chấp nhận yêu cầu". Đây đúng là khoảng trống mà breadcrumb tiêu đề của thành viên 1 lấp được — và cũng là chỗ breadcrumb phản tác dụng khi tiêu đề mô tả sai nội dung.

### So Sánh Giữa Các Thành Viên

Cùng corpus 10 tài liệu, cùng 5 câu hỏi, cùng embedder `LocalEmbedder` (`paraphrase-multilingual-MiniLM-L12-v2`). Chỉ khác chiến lược chia nhỏ.

| Thành viên | Chiến lược (Strategy) | Số chunk | Độ dài TB | Điểm từng câu | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|---------|-----------|---------------|----------------------|-----------|----------|
| Trần Xuân Đức | `RecursiveChunker` (800) | 58 | 665 | 1, 2, 2, 2, 2 | **9** | Tôn trọng ranh giới ngữ nghĩa mà không cần nguồn có tiêu đề; là chiến lược duy nhất không bị 0 điểm ở câu nào | Không mang ngữ cảnh mục cha, nên câu 1 chỉ được 1 điểm thay vì 2 |
| Phạm Long Nhật | `HeadingChunker` (breadcrumb) | 60 | 681 | 0, 2, 2, 2, 2 | 8 | Chunk trùng khít điều khoản; breadcrumb giúp chunk lẻ tự mô tả được ngữ cảnh; chunk câu 2 chỉ 171 ký tự nên đáp án rất sắc | Phụ thuộc hoàn toàn vào chất lượng tiêu đề nguồn; trượt trọn câu 1 vì tiêu đề mục mô tả sai trọng tâm |
| Nguyễn Tiến Lượng | `SentenceChunker` (max=5) | 50 | 769 | 0, 2, 2, 2, 2 | 8 | Không bao giờ cắt giữa mệnh đề; cấu hình đơn giản, chỉ một tham số | Chunk không biết mình thuộc mục nào; trượt câu 1 ở mọi giá trị `max` |
| Lê Thanh Tình | `FixedSizeChunker` (500/100) | 99 | 480 | 1, 1, 2, 1, 2 | 7 | Luôn chạy được, không giả định gì về cấu trúc; không bị tiêu đề đánh lừa nên vào được top-3 ở câu 1 | Cắt ngang bảng và ngang câu; câu 2 chỉ được 1 điểm ở **mọi** cấu hình overlap |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> `RecursiveChunker` với `chunk_size=800` tốt nhất, 9/10 — và lý do nó thắng nói lên bản chất của chủ đề. Văn bản chính sách Shopee đã được soạn thành đoạn rõ ràng, nhưng sau khi crawl thì **tiêu đề mục bị mất định dạng** (8/10 tài liệu chỉ còn đúng một `#`), trong khi **ranh giới đoạn vẫn còn nguyên**. `RecursiveChunker` cắt theo đoạn nên bám đúng thứ còn sống sót; `HeadingChunker` bám vào thứ đã hỏng một nửa; `FixedSizeChunker` và `SentenceChunker` thì không bám vào gì cả.
>
> Nhưng xếp hạng theo tổng điểm che mất điều quan trọng hơn: **bốn chiến lược mạnh ở những câu khác nhau và bù trừ cho nhau**. Câu 1 chỉ có `RecursiveChunker` (cấu hình 500) và `FixedSizeChunker` ghi được điểm, vì đó là câu mà tiêu đề mục — "3. Phân loại phương án xử lý" — không hề nhắc tới thời hạn, nên mọi chiến lược dựa vào tiêu đề đều bị đánh lừa. Ngược lại câu 2 và câu 4 thì `HeadingChunker` và `SentenceChunker` lấy trọn 2 điểm còn `FixedSizeChunker` chỉ được 1, vì hai câu đó cần chunk gói gọn đúng một mục.
>
> Kết luận thực dụng của nhóm: không có chiến lược nào thắng tuyệt đối, và lựa chọn đúng phụ thuộc vào **phần cấu trúc nào của nguồn còn sống sót sau khi thu thập**. Nếu nhóm làm sạch tay toàn bộ 10 tài liệu để khôi phục tiêu đề (như đã làm với `shopee-refund-timeline`), thứ hạng gần như chắc chắn sẽ đảo — vì đó chính là điều đã xảy ra với tài liệu đó: sau khi thêm heading cho từng phương thức hoàn tiền, `HeadingChunker` tách được 1 chunk thành 11 và lấy trọn 2 điểm ở câu 2.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sau khi Shopee chấp nhận yêu cầu Trả hàng & Hoàn tiền, người mua phải gửi trả sản phẩm trong bao lâu? | "Nếu Shopee đồng ý cho bạn Trả hàng & Hoàn tiền: Bạn cần chọn hình thức trả hàng và hoàn tất việc gửi trả hàng về kho Shopee/Người bán trong vòng **6 ngày** kể từ thời điểm nhận được thông báo gửi trả hàng từ Shopee." | `shopee-return-process`, mục `3. Phân loại phương án xử lý Trả hàng/ Hoàn tiền của Shopee` |
| 2 | Với đơn hàng thanh toán bằng thẻ tín dụng/ghi nợ, người mua nhận tiền hoàn trong bao lâu? | "Thẻ tín dụng/ghi nợ: **7 - 14 ngày làm việc** (tùy theo ngân hàng)." | `shopee-refund-timeline`, mục `Thẻ tín dụng/ghi nợ` |
| 3 | Khi tải bằng chứng cho yêu cầu Trả hàng/Hoàn tiền, dung lượng video tối đa được Shopee quy định là bao nhiêu? | "Dung lượng tối đa: Hình ảnh: Không quá 5MB/ảnh. Video: **Không quá 100 MB/video** (tối đa 1 phút)." | `shopee-return-evidence`, mục `4. Quy định về bằng chứng` |
| 4 | Những nhóm sản phẩm nào không áp dụng lý do trả hàng "Đổi ý"? | "Đối với nhóm sản phẩm này, Shopee không áp dụng lý do trả hàng 'Đổi ý (Sản phẩm còn nguyên tem, nhãn mác, bao bì)'." Bốn nhóm được liệt kê: "Sức khỏe, Vệ sinh & Đồ cá nhân", "Thực phẩm & Hàng mau hỏng", "Hàng đặc thù trong vận chuyển", "Sản phẩm số và dịch vụ". | `shopee-return-restrictions`, chunk duy nhất của tài liệu |
| 5 | Nếu không đồng ý với quyết định hoàn tiền, thời hạn phản hồi của người bán là bao lâu? | "Người Bán cần **phản hồi trong vòng 2 ngày lịch** kể từ ngày nhận thông báo nếu không đồng ý với quyết định hoàn tiền; chưa nhận được sản phẩm hoàn trả; sản phẩm không thuộc trường hợp được hoàn; hoặc sản phẩm bị hư hỏng, mất mát trong quá trình hoàn trả." | `shopee-return-policy-seller`, mục `Thời hạn phản hồi của người bán` — **cần `metadata_filter={"audience": "seller"}`** |

Cả 5 câu trả lời chuẩn đã được đối chiếu ngược lại corpus bằng `grep`, trích nguyên văn, không câu nào là suy đoán chính sách.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Thời hạn gửi trả sản phẩm sau khi được chấp nhận | `RecursiveChunker` (500) — **2đ**, cấu hình duy nhất của cả nhóm lấy trọn điểm câu này | Có, với Recursive và Fixed. **Không** với Heading và Sentence | Câu khó nhất. Đáp án nằm dưới tiêu đề "3. Phân loại phương án xử lý" — tiêu đề không nhắc gì tới thời hạn, nên breadcrumb kéo vector đi chệch. Với `HeadingChunker`, chunk đúng rơi xuống hạng 13/60 (score 0.717 so với top-1 là 0.825) |
| 2 | Thời gian hoàn tiền cho thẻ tín dụng/ghi nợ | `HeadingChunker` — **2đ**, chunk chỉ 171 ký tự chứa đúng một phương thức. `Sentence` (max=5) và `Recursive` (800) cũng 2đ | Có ở cả 4 chiến lược | `FixedSizeChunker` chỉ được 1đ ở **mọi** cấu hình overlap: tài liệu liệt kê 8 phương thức liên tiếp, cắt theo 500 ký tự gộp 3–4 phương thức vào một chunk nên không chunk nào đặc trưng cho riêng thẻ tín dụng |
| 3 | Dung lượng video tối đa của bằng chứng | Hòa — cả 4 chiến lược đều **2đ** | Có ở cả 4 | Câu dễ nhất. Đáp án nằm gọn trong một mục có tiêu đề mô tả đúng nội dung ("4. Quy định về bằng chứng"), nên chiến lược nào cũng khoanh trúng |
| 4 | Nhóm sản phẩm không áp dụng lý do "Đổi ý" | `HeadingChunker`, `Sentence`, `Recursive` (800) — **2đ** | Có ở cả 4 | `FixedSizeChunker` chỉ 1đ vì tài liệu `shopee-return-restrictions` ngắn (1.354 ký tự) và liệt kê 4 nhóm sản phẩm rải đều; cắt theo độ dài xé danh sách làm đôi |
| 5 | Thời hạn phản hồi của người bán (lọc `audience: seller`) | Hòa — cả 4 chiến lược đều **2đ** | Có ở cả 4 | Câu này do `metadata_filter` quyết định chứ không phải chunking: lọc xong chỉ còn 1 tài liệu nên chiến lược nào cũng trúng. Chi tiết ở phần dưới |

**Điểm cao nhất nhóm đạt được:** 9/10 (`RecursiveChunker` 800). Nếu ghép điểm tốt nhất của từng câu trên toàn nhóm thì được **10/10** — câu 1 lấy từ `RecursiveChunker` (500), bốn câu còn lại từ `HeadingChunker`. Điều này cho thấy một hệ thống thật nên kết hợp nhiều chiến lược chia nhỏ thay vì chọn một.

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, rõ nhất ở câu 5 — câu duy nhất hỏi về nghĩa vụ của người bán. Với `metadata_filter={"audience": "seller"}`, không gian tìm kiếm thu từ 60 chunk xuống còn 6 chunk của `shopee-return-policy-seller`, và cả top-3 đều nằm trong tài liệu đúng đối tượng.
> Lý do cần lọc chứ không phó mặc cho embedding: nhóm đo độ tương tự giữa "Người mua có 7 ngày để gửi yêu cầu trả hàng" và "Người bán phải phản hồi khiếu nại trong 2 ngày lịch" được **0.506** — gần như không phân biệt nổi. Hai câu này cùng chủ đề, cùng cấu trúc, cùng nói về một mốc thời gian; thứ khác nhau là *ai* phải làm, mà đó đúng là thứ embedding không mã hóa tốt. Không lọc thì câu 5 rất dễ trả về điều khoản dành cho người mua.
> Mặt trái cần nói thật: corpus hiện lệch 9 `buyer` / 1 `seller`, nên khi lọc `seller` thì chỉ còn đúng một tài liệu — câu 5 gần như chắc chắn trúng, và vì thế nó không phân biệt được chiến lược chunking giữa các thành viên. Nếu mở rộng corpus, nhóm nên bổ sung tài liệu `seller` để phép lọc vừa có ý nghĩa vừa còn tính cạnh tranh.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> **1. Chỉ số theo ngưỡng che giấu tiến bộ thật.** Tăng overlap của `FixedSizeChunker` từ 0 lên 100 kéo chunk chứa đáp án câu 2 từ hạng 9/60 lên hạng 4/60 — cải thiện rõ ràng và gần như đơn điệu. Nhưng vì rubric chấm theo top-3, cải thiện này không đổi được một điểm nào, và nhìn vào bảng điểm sẽ kết luận sai rằng overlap vô dụng. Nếu đo bằng MRR hoặc Recall@5, kết luận sẽ ngược lại.
>
> **2. Chất lượng chunking bị quyết định từ khâu thu thập dữ liệu, không phải khâu chọn thuật toán.** Crawler làm mất định dạng tiêu đề ở 8/10 tài liệu và làm phẳng hoàn toàn một bảng. Chính vì vậy `RecursiveChunker` (bám ranh giới đoạn — thứ còn sống sót) thắng `HeadingChunker` (bám tiêu đề — thứ đã hỏng). Nhóm chứng minh được chiều ngược lại: sau khi làm sạch tay `shopee-refund-timeline` để khôi phục heading, `HeadingChunker` tách 1 chunk thành 11 và lấy trọn 2 điểm ở câu đó.
>
> **3. Có những khác biệt embedding không mã hóa được, phải xử lý bằng metadata.** Hai câu "Người mua có 7 ngày để gửi yêu cầu trả hàng" và "Người bán phải phản hồi khiếu nại trong 2 ngày lịch" đạt độ tương tự 0.506 — gần như không phân biệt nổi, dù chủ thể hoàn toàn khác nhau. Đây là lý do `search_with_filter` tồn tại, và là lý do trường `audience` được thiết kế ngay từ khâu thu thập chứ không phải thêm vào sau.

**Bài học rút ra khi so sánh trong nhóm:**
> Khoảng cách tổng điểm giữa bốn chiến lược rất hẹp — 7, 8, 8, 9 trên thang 10 — nhưng **phân bố điểm theo từng câu thì khác hẳn nhau**. `HeadingChunker` và `SentenceChunker` cùng được 8 điểm với đúng cùng một dạng `0, 2, 2, 2, 2`, trong khi `FixedSizeChunker` được 7 điểm theo dạng `1, 1, 2, 1, 2` — tức là điểm thấp hơn nhưng lại **không trượt câu nào**. Nếu tiêu chí là "không bao giờ bỏ sót hoàn toàn", `FixedSizeChunker` mới là lựa chọn an toàn nhất, dù tổng điểm thấp nhất.
>
> Bài học thứ hai: **điểm mạnh và điểm yếu đối xứng nhau**. Breadcrumb tiêu đề giúp `HeadingChunker` thắng ở câu 2 và câu 4, và chính nó làm `HeadingChunker` trượt câu 1 khi tiêu đề mục mô tả sai trọng tâm phần thân. Không có tham số nào chỉnh được điều đó — nó là hệ quả trực tiếp của giả định mà chiến lược đặt ra về dữ liệu.
>
> Bài học thứ ba: **hướng chỉnh tham số không giống nhau giữa các chiến lược**. Với `FixedSizeChunker`, chunk nhỏ hơn thì tốt hơn (300 được 8, 800 được 7). Với `RecursiveChunker` thì ngược lại (300 được 8, 800 được 9). Lý do là chunk lớn ở `Recursive` nghĩa là giữ trọn một đoạn, còn chunk lớn ở `Fixed` chỉ đơn thuần trộn thêm nội dung không liên quan. Không thể mang trực giác chỉnh tham số từ chiến lược này sang chiến lược khác.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> **Cân bằng `audience` ngay từ đầu.** Corpus hiện lệch 9 `buyer` / 1 `seller`, nên câu 5 sau khi lọc chỉ còn đúng một tài liệu — cả 4 chiến lược đều trúng và câu đó mất hoàn toàn khả năng phân biệt. Nhóm sẽ thu thập thêm 3–4 tài liệu dành cho người bán để phép lọc vừa có ý nghĩa vừa còn tính cạnh tranh.
>
> **Làm sạch tay toàn bộ, không chỉ tài liệu hỏng nặng nhất.** Nhóm chỉ khôi phục heading cho `shopee-refund-timeline` vì nó hỏng rõ nhất, nhưng 7 tài liệu khác vẫn còn mục điều khoản nằm dưới dạng dòng văn bản thường. Đây là biến gây nhiễu lớn nhất trong toàn bộ phép so sánh: nó làm lợi cho các chiến lược không dựa vào tiêu đề và làm hại chiến lược dựa vào tiêu đề, nên kết quả đo được phản ánh chất lượng thu thập nhiều hơn là chất lượng thuật toán.
>
> **Thiết kế bộ câu hỏi đánh giá khó hơn và đo bằng nhiều chỉ số.** Ba trong năm câu được cả 4 chiến lược trả lời đúng, nên chỉ còn 2 câu thực sự phân biệt được — cỡ mẫu quá nhỏ để kết luận chắc chắn. Nhóm sẽ dùng 10–15 câu, cố ý bao gồm câu mà tiêu đề mục mô tả sai nội dung, và đo thêm MRR bên cạnh Hit@3 để không bỏ sót những cải thiện nằm dưới ngưỡng.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
