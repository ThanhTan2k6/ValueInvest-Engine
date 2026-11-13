## ValueInvest-Engine Pull Request

### 1. Phân loại Thay đổi (Type of Change)
- [ ] `feat`: Tính năng mới
- [ ] `fix`: Sửa lỗi công thức hoặc bug kỹ thuật
- [ ] `refactor`: Tái cấu trúc code (không đổi logic tính toán)
- [ ] `test`: Thêm/sửa unit tests hoặc evaluation cases
- [ ] `docs`: Cập nhật tài liệu kỹ thuật hoặc specs
- [ ] `ci`: Thay đổi cấu hình CI/CD workflow

---

### 2. Mô tả Tóm tắt Thay đổi (Summary & Context)
<!-- Nêu ngắn gọn nội dung PR, module bị ảnh hưởng và lý do thực hiện -->

---

### 3. Decoupled Architecture & Financial Guardrails Checklist
*Bắt buộc kiểm tra và đánh dấu toàn bộ trước khi yêu cầu Review:*

- [ ] **Kiểm tra Ranh giới Kiến trúc (Zero Math Hallucination)**:
  - Các file trong `src/engine/` và `src/valuation/` **không** import thư viện LLM (`langchain`, `openai`, `langgraph`, v.v.).
  - LLM chỉ tiếp nhận số liệu đã tính toán sẵn qua JSON/Pydantic, không tự thực hiện phép tính số học (ROE, WACC, DCF, MoS).
- [ ] **Toàn vẹn Dữ liệu Kế toán (VAS Circular 200/2014/TT-BTC)**:
  - Mọi BCTC sau khi sanitize đảm bảo: $\text{Assets} = \text{Liabilities} + \text{Equity}$ (sai số $< 10^{-4}$).
- [ ] **Xử lý Edge Cases Tài chính**:
  - Đã xử lý trường hợp chia cho 0 (ví dụ: Chi phí lãi vay = 0 khi tính Interest Coverage).
  - Đã xử lý trường hợp số âm bất thường (Vốn chủ sở hữu âm $\le 0$).
- [ ] **Bộ lọc Pháp lý & Disclaimer**:
  - Không chứa các phát ngôn khuyến nghị mua/bán trực tiếp ("Khuyến nghị Mua", "Khuyến nghị Bán", "Target price").
  - Mọi báo cáo tự động gắn kèm Disclaimer theo quy định của UBCKNN.

---

### 4. Kết quả Kiểm thử & Quality Gate (Verification)
- [ ] `ruff check src/ tests/` đã chạy và không có lỗi (0 errors, 0 warnings).
- [ ] Unit Test Coverage trên `src/engine/` và `src/valuation/` đạt $> 80\%$.
- [ ] DeepEval Faithfulness Score đạt $\ge 0.95$ trên bộ Golden Dataset (nếu PR chạm vào `src/agents/` hoặc prompts).
- [ ] Docker build chạy thử thành công cục bộ: `docker-compose build`.

---

### 5. Issues Liên quan (Related Issues)
Closes #
