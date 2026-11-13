# Technical Specification 00: Functional & Edge-Case Blueprint (`spec_00_use_cases.md`)
> **Project:** ValueInvest-Engine  
> **Role:** Principal AI Systems Architect & Quantitative FinTech Tech Lead  
> **Standard:** Spec-Driven Development, BDD Acceptance Criteria, Zero Math Hallucination

---

## Danh mục Use Cases Cốt lõi
* **UC-01:** Tra cứu & Chuẩn hóa Báo cáo Tài chính (`Ingest & Sanitize`)
* **UC-02:** Kiểm toán Sức khỏe Tài chính & Quét Bẫy Kế toán (`Health Check & Red Flags`)
* **UC-03:** Định giá DCF Đa kịch bản & Ma trận Độ nhạy (`Dynamic Valuation & Sensitivity`)
* **UC-04:** Kích hoạt Hội đồng Phản biện Đa tác tử (`Socratic Devil's Advocate`)
* **UC-05:** Xuất Báo cáo Đầu tư One-Pager (`Export Investment Memo`)

---

# USE CASE 01: Tra cứu & Chuẩn hóa Báo cáo Tài chính (`Ingest & Sanitize`)

### 1. Metadata & SLA
- **Use Case ID:** `UC-01`
- **Tên Use Case:** Tra cứu, thu thập và chuẩn hóa dữ liệu BCTC doanh nghiệp niêm yết theo Thông tư 200/2014/TT-BTC.
- **Module phụ trách:** `src/ingestion/vnstock_loader.py`, `src/ingestion/sanitizer.py`
- **Input Schema:** `ticker: str` (e.g. `"HPG"`), `lookback_years: int = 5`, `period_type: Literal["FY", "Q"] = "FY"`
- **Output Schema:** `FinancialStatementSchema` (tham chiếu [spec_01_data_contracts.md](file:///d:/ValueInvest-Engine/.specs/spec_01_data_contracts.md#L1-L125))
- **Cam kết Độ trễ (SLA Latency):** 
  - Cold Fetch (gọi API ngoài `vnstock`/Vietstock): $\le 2.0\text{s}$ cho 5 năm dữ liệu BCTC.
  - Warm Fetch (Hit local parquet / disk-cache): $\le 0.1\text{s}$.

### 2. Pre-conditions & Post-conditions
- **Pre-conditions:**
  - Người dùng nhập chuỗi ký tự mã cổ phiếu (3–5 ký tự in hoa) vào ô tìm kiếm trên Dashboard.
  - Kết nối mạng tới nguồn dữ liệu khả dụng hoặc đã có file cache trong `data/cache/`.
- **Post-conditions:**
  - Dữ liệu BCTC đã được làm sạch, kiểm định đẳng thức kế toán, ép kiểu thành công vào `FinancialStatementSchema`.
  - Đối tượng dữ liệu được lưu vào Session State của ứng dụng và ghi bản sao vào disk cache `data/cache/{ticker}_bctc.parquet`.

### 3. Main Success Scenario (Luồng chuẩn)
1. **Step 1 (User Action):** Người dùng nhập mã `HPG` trên Streamlit UI và nhấn `Analyze`.
2. **Step 2 (API Gateway):** Streamlit gửi `GET /api/v1/statements/HPG?years=5` tới FastAPI Controller.
3. **Step 3 (Cache Check):** `vnstock_loader` kiểm tra `data/cache/HPG_bctc.parquet`. Nếu còn hiệu lực trong ngày giao dịch (TTL 24h), nạp trực tiếp; nếu không, gọi API `vnstock`.
4. **Step 4 (Data Ingestion):** Tải 3 bảng tài chính: Cân đối kế toán (B01-DN), Kết quả kinh doanh (B02-DN), Lưu chuyển tiền tệ gián tiếp (B03-DN) cùng text trích xuất Thuyết minh BCTC.
5. **Step 5 (Sanitization & Alignment):** `sanitizer.py` chuẩn hóa mã tài khoản theo Thông tư 200, chuyển đổi đơn vị về VND, điền 0.0 cho các dòng phụ không bắt buộc, xác thực đẳng thức: $\text{Tài sản} = \text{Nguồn vốn}$.
6. **Step 6 (Contract Validation):** Nạp vào Pydantic model `FinancialStatementSchema` với cấu hình `frozen=True, strict=True`.
7. **Step 7 (UI Render):** Trả về HTTP 200 kèm JSON; Streamlit render bảng tóm tắt lịch sử 5 năm doanh thu, lợi nhuận và tổng tài sản.

### 4. Alternative Flows
- **AF 1.1 - Hit Raw Disk Cache:** Tại Step 3, nếu phát hiện file cache `data/cache/{ticker}_bctc.parquet` được tạo cách đây dưới 24 giờ, hệ thống bỏ qua bước gọi API mạng, deserialized trực tiếp thành schema và chuyển sang Step 6. Độ trễ $< 50\text{ms}$.
- **AF 1.2 - Offline Ingestion via Local Excel/JSON:** Trong môi trường không có internet, hệ thống nạp dữ liệu từ thư mục `data/raw/{ticker}.xlsx`. Quy trình sanitize và validate diễn ra tương đương.

### 5. Exception & Financial Edge Cases

| Mã lỗi / Tình huống | Điều kiện kích hoạt | Hành vi xử lý bắt buộc của hệ thống | Thông báo hiển thị UI |
|---|---|---|---|
| `ERR_TICKER_NOT_FOUND` | Mã nhập vào không nằm trong danh bạ niêm yết HOSE/HNX/UPCOM (e.g. `"XYZ123"`). | `vnstock_loader` bắt lỗi `404/EmptyDataFrame`, chặn pipeline không gọi sanitizer. Trả về HTTP 404. | ❌ Mã cổ phiếu không tồn tại trên sàn chứng khoán Việt Nam. Vui lòng kiểm tra lại. |
| `ERR_FINANCIAL_SECTOR_UNSUPPORTED` | Doanh nghiệp thuộc nhóm Ngân hàng (Mã ngành ICB 8300), Bảo hiểm (8500), Chứng khoán (8700). | Kiểm tra metadata phân ngành ICB. Hệ thống từ chối nạp vì chuẩn kế toán Ngân hàng (QĐ 479/2004/NHNN) không tuân theo Thông tư 200 (không có Doanh thu thuần, Giá vốn, Nợ chiếm dụng tiêu chuẩn). | ⚠️ Hệ thống hiện chỉ hỗ trợ doanh nghiệp sản xuất, thương mại, dịch vụ phi tài chính theo Thông tư 200/BTC. Chưa hỗ trợ Ngân hàng và Bảo hiểm. |
| `ERR_ACCOUNTING_EQUATION_MISMATCH` | Chênh lệch $\|\text{Total Assets} - \text{Total Resources}\| > 10^{-4}$ tại bất kỳ kỳ báo cáo nào. | `@model_validator` trong `BalanceSheetItem` ném ra `AccountingBalanceError`. Dừng toàn bộ pipeline, cấm đưa dữ liệu rác vào Math Engine. | 🚫 Lỗi toàn vẹn kế toán: Bảng cân đối kế toán kỳ {period} không cân bằng. Hệ thống từ chối phân tích để bảo vệ nhà đầu tư. |
| `ERR_DATA_VENDOR_TIMEOUT` | API vendor (`vnstock`/Vietstock) không phản hồi sau $5.0\text{s}$ hoặc trả về HTTP 429 (Rate Limit). | Áp dụng Tenacity Retry 3 lần với Exponential Backoff (1s, 2s, 4s). Nếu vẫn thất bại, kiểm tra cache phiên trước. Nếu không có cache, trả về HTTP 504. | ⚠️ Kết nối tới máy chủ dữ liệu BCTC bị gián đoạn. Đang tự động thử lại hoặc vui lòng tải lại sau ít phút. |
| `ERR_INCOMPLETE_TIME_SERIES` | Doanh nghiệp mới niêm yết có dưới 3 kỳ BCTC năm. | `sanitizer` kiểm tra `len(balance_sheets) < 3`. Cho phép hiển thị dữ liệu lịch sử nhưng vô hiệu hóa tính toán biến thiên 3 năm, hiển thị cảnh báo thiếu hụt chuỗi dữ liệu. | ⚠️ Doanh nghiệp niêm yết dưới 3 năm. Một số chỉ báo xu hướng dài hạn sẽ bị giới hạn. |

### 6. Acceptance Criteria (BDD Tests)

#### Scenario 1.1: Happy Path - Ingest & Sanitize BCTC của HPG thành công
```gherkin
Given Mã cổ phiếu "HPG" hợp lệ trên sàn HOSE
And Máy chủ có kết nối internet hoặc có cache dữ liệu
When Người dùng gửi yêu cầu phân tích dữ liệu 5 năm gần nhất
Then Hệ thống trả về đối tượng FinancialStatementSchema với đúng 5 kỳ BCTC
And Mỗi kỳ BCTC đều thỏa mãn tuyệt đối: Assets == Liabilities + Equity với sai số < 1e-4
And Toàn bộ thời gian xử lý không vượt quá 2.0 giây
```

#### Scenario 1.2: Exception - Mã thuộc ngành Ngân hàng (VCB)
```gherkin
Given Mã cổ phiếu "VCB" thuộc nhóm Ngân hàng thương mại
When Người dùng nhấn Analyze
Then Hệ thống phát hiện phân ngành ICB là "Banks"
And Chặn không cho nạp vào sanitizer Thông tư 200
And Trả về mã lỗi ERR_FINANCIAL_SECTOR_UNSUPPORTED
And Hiển thị thông báo giải thích rõ hệ thống chưa hỗ trợ chuẩn kế toán ngân hàng
```

#### Scenario 1.3: Exception - BCTC mất cân đối kế toán do dữ liệu crawl bị lỗi
```gherkin
Given Một tệp BCTC thô của mã "ABC" bị sai lệch do lỗi nhập liệu: Tổng tài sản = 1.000 tỷ, Tổng nguồn vốn = 990 tỷ
When sanitizer.py thực thi kiểm định cân đối kế toán
Then Hệ thống ném ngoại lệ ValueError("Lỗi cân đối BCTC...")
And Chặn không tạo đối tượng FinancialStatementSchema
And Không cho phép chuyển dữ liệu sang Deterministic Math Engine
```

---

# USE CASE 02: Kiểm toán Sức khỏe Tài chính & Quét Bẫy Kế toán (`Health Check & Red Flags`)

### 1. Metadata & SLA
- **Use Case ID:** `UC-02`
- **Tên Use Case:** Phân rã DuPont 3 bước và quét toàn bộ các bẫy kế toán định lượng (Traffic Light Red Flags).
- **Module phụ trách:** `src/engine/dupont.py`, `src/engine/red_flags.py`, `src/engine/metrics.py`, `src/engine/cashflow.py`
- **Input Schema:** `FinancialStatementSchema` (từ UC-01)
- **Output Schema:** `RedFlagReportSchema` (tham chiếu [spec_01_data_contracts.md](file:///d:/ValueInvest-Engine/.specs/spec_01_data_contracts.md#L127-L157))
- **Cam kết Độ trễ (SLA Latency):** $\le 0.5\text{s}$ (Toán thuần túy NumPy/Pandas, hoàn toàn không phụ thuộc I/O mạng).

### 2. Pre-conditions & Post-conditions
- **Pre-conditions:** `UC-01` hoàn thành thành công, đã có đối tượng `FinancialStatementSchema` hợp lệ trong bộ nhớ.
- **Post-conditions:** 
  - Tạo thành công đối tượng `RedFlagReportSchema` chứa danh sách cờ cảnh báo (Critical / Warning / Safe).
  - Tách sẵn các đoạn text Thuyết minh trọng yếu liên quan tới các cờ Critical để chuyển tiếp cho UC-04.

### 3. Main Success Scenario (Luồng chuẩn)
1. **Step 1 (Trigger):** Sau khi UC-01 hoàn tất, FastAPI Controller tự động chuyển `FinancialStatementSchema` sang `src/engine/`.
2. **Step 2 (DuPont Calculation):** `dupont.py` tính toán chuỗi chỉ số 3 nhân tố: $\text{ROE} = \text{Net Margin} \times \text{Asset Turnover} \times \text{Financial Leverage}$ cho từng kỳ, sử dụng số dư bình quân giữa 2 kỳ liên tiếp.
3. **Step 3 (Cash Flow & Solvency Metrics):** `cashflow.py` và `metrics.py` tính toán CFO, Interest Coverage Ratio, Net Debt / Equity, Current Ratio, Quick Ratio, DSO, DSI.
4. **Step 4 (Red Flags Scanning):** `red_flags.py` duyệt song song qua 6 bộ quy tắc định lượng:
   - *Quy tắc 1 (Critical):* $\text{NPAT} > 0$ và $\text{CFO} < 0$ liên tục 2 kỳ trở lên.
   - *Quy tắc 2 (Critical):* $\text{Nợ ngắn hạn chịu lãi} > 1.5 \times (\text{Tiền} + \text{Đầu tư ngắn hạn})$ và $\text{Current Ratio} < 1.0$.
   - *Quy tắc 3 (Critical):* Phải thu khác tăng trưởng $> 2.0 \times \text{Tăng trưởng doanh thu}$.
   - *Quy tắc 4 (Warning):* Tỷ lệ $\frac{\text{Phải thu}}{\text{Doanh thu}} > 1.5 \times \text{Mức bình quân 3 năm}$.
   - *Quy tắc 5 (Warning):* Biên lợi nhuận gộp sụt giảm liên tiếp 3 năm tài chính.
   - *Quy tắc 6 (Safe):* Interest Coverage $\ge 5.0x$.
5. **Step 5 (Report Generation):** Đóng gói thành `RedFlagReportSchema`, gắn nhãn mức độ nghiêm trọng (Traffic Light).
6. **Step 6 (UI Render):** Streamlit hiển thị Dashboard với các thẻ Badge màu (Đỏ/Vàng/Xanh) cùng biểu đồ phân rã DuPont tương tác.

### 4. Alternative Flows
- **AF 2.1 - Clean Financials (Zero Red Flags):** Doanh nghiệp có sức khỏe tài chính hoàn hảo (ví dụ: VNM giai đoạn hoàng kim), không kích hoạt cờ Critical hoặc Warning nào. Hệ thống đánh dấu trạng thái `FINANCIALLY_SOUND`, hiển thị badge Safe toàn bộ và bật cờ cho phép định giá Base/Bull tại UC-03.

### 5. Exception & Financial Edge Cases

| Mã lỗi / Tình huống | Điều kiện kích hoạt | Hành vi xử lý bắt buộc của hệ thống | Thông báo hiển thị UI |
|---|---|---|---|
| `EDGE_ZERO_INTEREST_EXPENSE` | Doanh nghiệp hoàn toàn không có nợ vay, chi phí lãi vay trên P&L = 0 (Mã 23 = 0). | Mẫu số bằng 0 khi tính $\text{Interest Coverage} = \frac{\text{EBIT}}{\text{Lãi vay}}$. Hệ thống gán giá trị Sentinel `float("inf")` (hoặc `999.0`), kích hoạt cờ Safe: `DEBT_FREE_COVERAGE`. Tuyệt đối không để crash `ZeroDivisionError`. | 🟢 Doanh nghiệp không sử dụng nợ vay chịu lãi. Hệ số phủ lãi vay: Tuyệt đối an toàn. |
| `EDGE_DISTRESSED_NEGATIVE_EQUITY` | Doanh nghiệp lỗ lũy kế vượt vốn điều lệ, dẫn đến Tổng vốn chủ sở hữu $\le 0$ (e.g. HVN, TTF). | Khi $Equity \le 0$, mẫu số DuPont bị âm gây đảo dấu toán học. Hệ thống gán `financial_leverage = None`, `roe = None`, đồng thời kích hoạt ngay lập tức cờ Critical `CRIT_NEGATIVE_EQUITY`. | 🔴 BÁO ĐỘNG ĐỎ: Vốn chủ sở hữu âm do lỗ lũy kế kéo dài. Doanh nghiệp mất an toàn vốn nghiêm trọng. |
| `EDGE_NEGATIVE_REVENUE_OR_PROFIT` | Doanh nghiệp kinh doanh thua lỗ, Net Income $< 0$. | Tỷ số Net Margin mang dấu âm. Hệ thống cho phép hiển thị số âm nhưng vô hiệu hóa cờ Safe tăng trưởng, bật cảnh báo lợi nhuận âm. | 🟡 Cảnh báo: Doanh nghiệp ghi nhận lỗ thuần trong kỳ. Tỷ suất lợi nhuận ròng âm. |
| `WARN_MISSING_NOTES_TEXT` | Dữ liệu nạp vào không có phần text trích xuất Thuyết minh BCTC (`notes_extracts == {}`). | Vẫn hoàn thành 100% tính toán số học Red Flags định lượng; đánh dấu cờ `notes_available = False` để báo cho UC-04 chỉ phản biện trên số liệu mà không trích xuất chi tiết Thuyết minh. | ℹ️ Dữ liệu Thuyết minh dạng text chưa sẵn sàng. Đang phân tích rủi ro dựa trên số liệu định lượng BCTC. |

### 6. Acceptance Criteria (BDD Tests)

#### Scenario 2.1: Happy Path - Phát hiện cờ Đỏ Lợi nhuận giấy (CFO Divergence) trên NVL
```gherkin
Given BCTC của NVL năm 2022 có NPAT = 2.181 tỷ VND (> 0) và CFO = -3.262 tỷ VND (< 0)
And Năm 2021 trước đó CFO cũng âm -2.800 tỷ VND
When red_flags.py thực thi quét bẫy kế toán
Then Hệ thống kích hoạt SingleRedFlagTrigger với flag_id "CRIT_CFO_DIVERGENCE"
And Mức độ severity được đặt là "CRITICAL"
And Báo cáo ghi rõ bằng chứng: Lợi nhuận dương nhưng dòng tiền kinh doanh âm 2 năm liên tiếp
```

#### Scenario 2.2: Edge Case - Doanh nghiệp không vay nợ, chi phí lãi vay bằng 0
```gherkin
Given BCTC của doanh nghiệp không phát sinh nợ vay, Mã 23 (Chi phí lãi vay) = 0.0
And Lợi nhuận trước lãi vay và thuế (EBIT) = 500 tỷ VND
When metrics.py tính toán Interest Coverage Ratio
Then Hệ thống không ném ngoại lệ ZeroDivisionError
And Kết quả interest_coverage_ratio trả về giá trị an toàn tuyệt đối (>= 999.0)
And Cờ SAFE_INTEREST_COVERAGE được kích hoạt
```

#### Scenario 2.3: Edge Case - Vốn chủ sở hữu âm do lỗ lũy kế vượt vốn góp
```gherkin
Given BCTC của công ty có Tổng tài sản = 5.000 tỷ VND, Nợ phải trả = 6.000 tỷ VND
And Tổng vốn chủ sở hữu = -1.000 tỷ VND
When dupont.py tính toán phân rã ROE và Đòn bẩy tài chính
Then Hệ thống trả về financial_leverage = None và roe = None
And Kích hoạt cờ CRIT_NEGATIVE_EQUITY với severity "CRITICAL"
And Trường is_distressed_equity trong kết quả được bật True
```

---

# USE CASE 03: Định giá DCF Đa kịch bản & Ma trận Độ nhạy (`Dynamic Valuation & Sensitivity`)

### 1. Metadata & SLA
- **Use Case ID:** `UC-03`
- **Tên Use Case:** Tính toán mô hình định giá chiết khấu dòng tiền tự do (DCF), sinh ma trận độ nhạy 2 chiều và tính Biên an toàn (Margin of Safety).
- **Module phụ trách:** `src/valuation/dcf.py`, `src/valuation/sensitivity.py`, `src/valuation/scenarios.py`
- **Input Schema:** `DCFInputParams` (tham chiếu [spec_01_data_contracts.md](file:///d:/ValueInvest-Engine/.specs/spec_01_data_contracts.md#L159-L188))
- **Output Schema:** `ValuationOutputSchema` (tham chiếu [spec_01_data_contracts.md](file:///d:/ValueInvest-Engine/.specs/spec_01_data_contracts.md#L201-L215))
- **Cam kết Độ trễ (SLA Latency):** $\le 0.1\text{s}$ (100% Vectorized NumPy, tính ma trận $10 \times 10$ trong $< 20\text{ms}$).

### 2. Pre-conditions & Post-conditions
- **Pre-conditions:**
  - Dữ liệu tài chính đã được tính toán từ UC-01 & UC-02 để cung cấp FCF kỳ cơ sở, số lượng cổ phiếu lưu hành và nợ vay thuần.
  - Người dùng có thể giữ nguyên tham số mặc định (tính tự động theo CAPM) hoặc điều chỉnh các Sliders trên UI.
- **Post-conditions:**
  - Xuất ra bảng định giá 3 kịch bản: Bear, Base, Bull kèm giá trị nội tại mỗi cổ phiếu và Margin of Safety (MoS).
  - Xuất ra mảng 2D ma trận độ nhạy ($WACC$ biến thiên $10\% \to 14\%$, $g$ biến thiên $2\% \to 5\%$) sẵn sàng đưa vào Plotly Heatmap.

### 3. Main Success Scenario (Luồng chuẩn)
1. **Step 1 (Parameter Binding):** Dashboard Streamlit hiển thị các thanh trượt tham số:
   - Tăng trưởng FCF Giai đoạn 1 ($g_{stage1}$): mặc định $8.0\%$.
   - Chi phí vốn bình quân ($WACC$): mặc định tính theo CAPM (ví dụ $11.5\%$).
   - Tăng trưởng vĩnh viễn ($g_{terminal}$): mặc định $2.5\%$.
   - Số năm dự phóng ($N$): mặc định 5 năm.
2. **Step 2 (Pydantic Contract Check):** Khi người dùng kéo thanh trượt, đối tượng `DCFInputParams` được tạo và kiểm tra tính hợp lệ ($WACC > g_{terminal}$).
3. **Step 3 (Stage 1 PV Calculation):** `dcf.py` tính hiện giá của chuỗi dòng tiền tự do 5 năm tới:
   $$PV_{Stage 1} = \sum_{t=1}^{5} \frac{FCF_0 \times (1 + g_{stage1})^t}{(1 + WACC)^t}$$
4. **Step 4 (Terminal Value Calculation):** Tính giá trị kết thúc theo mô hình Gordon Growth và chiết khấu về hiện tại:
   $$TV = \frac{FCF_5 \times (1 + g_{terminal})}{WACC - g_{terminal}}, \quad PV_{TV} = \frac{TV}{(1 + WACC)^5}$$
5. **Step 5 (Equity Value & Per Share Value):**
   $$EV = PV_{Stage 1} + PV_{TV}, \quad Equity\ Value = EV - Net\ Debt$$
   $$Intrinsic\ Value = \frac{Equity\ Value}{Shares\ Outstanding}$$
6. **Step 6 (Margin of Safety Calculation):**
   $$MoS = \frac{Intrinsic\ Value - Current\ Price}{Intrinsic\ Value} \times 100\%$$
7. **Step 7 (2D Sensitivity Matrix Generation):** `sensitivity.py` thực thi NumPy broadcasting trên dải $WACC \in [10\%, 14\%]$ và $g \in [2\%, 5\%]$, sinh ma trận $10 \times 10$ giá trị cổ phiếu.
8. **Step 8 (Scenarios Construction):** `scenarios.py` tính tự động 3 mốc:
   - **Bear Case:** $g_{stage1} - 3\%$, $WACC + 1.5\%$.
   - **Base Case:** Theo tham số hiện hành.
   - **Bull Case:** $g_{stage1} + 3\%$, $WACC - 1.0\%$.
9. **Step 9 (UI Render):** Streamlit vẽ Plotly Waterfall Chart phân rã dòng tiền và Heatmap ma trận độ nhạy trong $< 100\text{ms}$.

### 4. Alternative Flows
- **AF 3.1 - User Slider Real-time Tweaking:** Người dùng thay đổi liên tục các slider $WACC$ hoặc $g$. Frontend gọi API endpoint chuyên biệt `POST /api/v1/valuation/recalculate` chỉ truyền tham số đầu vào mà không cần crawl lại BCTC. Thời gian render tức thì ($< 50\text{ms}$).

### 5. Exception & Financial Edge Cases

| Mã lỗi / Tình huống | Điều kiện kích hoạt | Hành vi xử lý bắt buộc của hệ thống | Thông báo hiển thị UI |
|---|---|---|---|
| `ERR_WACC_LE_TERMINAL_G` | Người dùng kéo slider khiến $WACC \le g_{terminal}$ (ví dụ: $WACC = 2.5\%$, $g = 3.0\%$). | Model validator trong `DCFInputParams` chặn đứng, ném `ValueError`. Hệ thống từ chối tính toán vì vi phạm điều kiện hội tụ toán học của Gordon Growth (mẫu số $\le 0$). | ⚠️ Lỗi toán học: Chi phí vốn WACC phải lớn hơn Tốc độ tăng trưởng vĩnh viễn (g) tối thiểu 0.5% để mô hình hội tụ. |
| `EDGE_CHRONIC_NEGATIVE_FCF` | Dòng tiền tự do FCF kỳ cơ sở $\le 0$ do thâm dụng CapEx hoặc kinh doanh bết bát. | Không được giả định số âm tăng trưởng âm thành dương. Hệ thống chuyển sang tính Normalized FCF (bình quân 3-5 năm) hoặc cảnh báo từ chối áp dụng DCF cơ bản, đề xuất dùng mô hình Asset-based / Liquidation Value. | ⚠️ FCF cơ sở đang âm do chi đầu tư CapEx lớn hoặc dòng tiền kinh doanh yếu. Kết quả DCF có thể không mang tính đại diện. |
| `EDGE_NEGATIVE_INTRINSIC_VALUE` | Nợ vay quá lớn ($Net\ Debt > Enterprise\ Value$) khiến Giá trị vốn chủ sở hữu âm. | Giá trị nội tại mỗi cổ phần không được hiển thị số âm (trách nhiệm hữu hạn của cổ đông). Hệ thống ép sàn về `0.0 VND/cp` và gán $MoS = -100.0\%$. | 🔴 Cảnh báo: Doanh nghiệp thâm dụng nợ nghiêm trọng. Giá trị vốn cổ phần theo mô hình DCF rơi về 0. |
| `ERR_ZERO_MARKET_PRICE` | Thị giá cổ phiếu bị lỗi dữ liệu hoặc tạm ngừng giao dịch trả về $\le 0$. | `DCFInputParams` có validator `current_market_price: PositiveFloat`. Hệ thống chặn tính MoS và hiển thị trạng thái không xác định được thị giá. | ⚠️ Không tìm thấy giá thị trường hợp lệ để tính Biên an toàn (Margin of Safety). |

### 6. Acceptance Criteria (BDD Tests)

#### Scenario 3.1: Happy Path - Tính toán DCF 3 kịch bản & Ma trận độ nhạy cho HPG
```gherkin
Given Tham số định giá: base_fcf = 10.000 tỷ VND, stage1_g = 8%, WACC = 11.5%, g_terminal = 2.5%
And Số lượng cổ phiếu = 5.8 tỷ, Nợ thuần = 25.000 tỷ, Thị giá = 28.000 VND
When dcf.py và sensitivity.py thực thi tính toán
Then Giá trị nội tại Base Case được tính toán chính xác
And Bảng định giá hiển thị đủ 3 kịch bản Bear, Base, Bull với MoS tương ứng
And Ma trận độ nhạy trả về mảng 2 chiều kích thước 10x10 không chứa giá trị NaN
And Toàn bộ phép tính hoàn tất trong dưới 50 mili-giây
```

#### Scenario 3.2: Exception - Slider vi phạm điều kiện WACC <= g_terminal
```gherkin
Given Người dùng thiết lập thanh trượt WACC = 2.5% và terminal_growth = 3.0%
When DCFInputParams tiếp nhận dữ liệu
Then Hệ thống ném ngoại lệ Pydantic ValidationError
And Chặn không gọi hàm tính toán terminal value
And Giao diện Streamlit hiển thị cảnh báo đỏ yêu cầu điều chỉnh WACC > g
```

#### Scenario 3.3: Edge Case - Nợ vay áp đảo Enterprise Value khiến Equity Value âm
```gherkin
Given Doanh nghiệp có Enterprise Value (EV) tính được là 15.000 tỷ VND
And Tổng nợ vay thuần (Net Debt) lên tới 25.000 tỷ VND
When dcf.py tính toán Intrinsic Value Per Share
Then Giá trị nội tại mỗi cổ phần được ép sàn về 0.0 VND thay vì số âm
And Biên an toàn Margin of Safety được xác định là -100.0%
And Kịch bản được phân loại là "EXPENSIVE"
```

---

# USE CASE 04: Kích hoạt Hội đồng Phản biện Đa tác tử (`Socratic Devil's Advocate`)

### 1. Metadata & SLA
- **Use Case ID:** `UC-04`
- **Tên Use Case:** Kích hoạt luồng Multi-Agent LangGraph thẩm định rủi ro Thuyết minh BCTC và phản biện Socratic các giả định định giá của nhà đầu tư.
- **Module phụ trách:** `src/agents/supervisor.py`, `src/agents/forensic.py`, `src/agents/challenger.py`, `src/llmops/guardrails.py`, `src/llmops/tracer.py`
- **Input Schema:** Context JSON tổng hợp từ UC-01, UC-02, UC-03 (`ticker`, `red_flags`, `valuation_outputs`, `extracted_notes`)
- **Output Schema:** `AgentCritiqueSchema` (tham chiếu [spec_01_data_contracts.md](file:///d:/ValueInvest-Engine/.specs/spec_01_data_contracts.md#L217-L255))
- **Cam kết Độ trễ (SLA Latency):**
  - Cache Hit (Redis Semantic Cache): $\le 0.2\text{s}$.
  - Cache Miss (Gọi song song GPT-4o / LangGraph): $\le 6.0\text{s}$ (kèm cơ chế Streaming Text).

### 2. Pre-conditions & Post-conditions
- **Pre-conditions:**
  - UC-01, UC-02, UC-03 đã chạy thành công; các chỉ số toán học đã đóng gói thành immutable JSON.
  - Người dùng bấm nút `Challenge My Valuation` trên Dashboard.
  - Cấu hình khóa API (`OPENAI_API_KEY`) hoặc dịch vụ LLM hợp lệ.
- **Post-conditions:**
  - Hoàn tất phiên phản biện đa tác tử được ghi log toàn bộ vào Langfuse Dashboard.
  - Kết quả được serialize và lưu vào Redis Cache với TTL 24h.
  - Xuất ra `AgentCritiqueSchema` với 3 câu hỏi Socratic sắc bén và Disclaimer kiểm duyệt.

### 3. Main Success Scenario (Luồng chuẩn)
1. **Step 1 (User Action):** Người dùng bấm nút `Challenge My Valuation` sau khi điều chỉnh các giả định định giá.
2. **Step 2 (Semantic Cache Lookup):** `src/llmops/tracer.py` tính toán SHA256 hash của bộ tham số: `(ticker, wacc, stage1_g, terminal_g)`. Nếu tồn tại trong Redis, trả về kết quả trong $< 0.2\text{s}$ (nhảy tới Step 8).
3. **Step 3 (Langfuse Trace Init):** Khởi tạo Root Trace trên Langfuse với `trace_name="ValueInvest_MultiAgent_Workflow"` để theo dõi latency và token cost.
4. **Step 4 (Supervisor Node):** `Supervisor Agent` tiếp nhận JSON, chuẩn bị payload và phân công đồng thời cho 2 sub-agents.
5. **Step 5 (Parallel Execution):**
   - **Forensic Auditor Agent:** Đọc các cờ Critical từ UC-02 và đoạn Thuyết minh nợ vay/bên liên quan; bóc tách bản chất rủi ro dòng tiền và tài sản.
   - **Valuation Challenger Agent:** Đóng vai Biện lý phản bác (Devil's Advocate), đối chiếu $g$ và $WACC$ của người dùng với lịch sử 3 năm qua; sinh ra 3 câu hỏi Socratic.
6. **Step 6 (Synthesis & Structured Output):** `Synthesis Node` tổng hợp các phản biện thành văn bản Markdown súc tích ($< 300$ từ), ép kiểu qua `instructor` vào schema `AgentCritiqueSchema`.
7. **Step 7 (Guardrails & Faithfulness Verification):**
   - Quét từ khóa: Kiểm tra không chứa các từ bị cấm ("Khuyến nghị Mua/Bán", "Target price").
   - Gắn cố định Disclaimer pháp lý UBCKNN.
   - Kiểm tra sơ bộ tính toàn vẹn số liệu (mọi con số phải nằm trong JSON đầu vào).
8. **Step 8 (Cache Update & UI Streaming):** Lưu kết quả vào Redis Cache. Streamlit render giao diện dạng hội đồng chất vấn với các câu hỏi nổi bật.

### 4. Alternative Flows
- **AF 4.1 - Redis Semantic Cache Hit:** Tại Step 2, phát hiện người dùng khác hoặc chính người dùng đó đã gửi yêu cầu thẩm định với cùng bộ tham số trong phiên. Hệ thống nạp từ Redis, hoàn toàn không gọi LLM API, tiết kiệm 100% token cost và trả về tức thì ($0.15\text{s}$).

### 5. Exception & Financial Edge Cases

| Mã lỗi / Tình huống | Điều kiện kích hoạt | Hành vi xử lý bắt buộc của hệ thống | Thông báo hiển thị UI |
|---|---|---|---|
| `ERR_LLM_TIMEOUT_OR_UNAVAILABLE` | LLM API (OpenAI/Anthropic) bị quá tải, timeout sau $8.0\text{s}$ hoặc trả về HTTP 500/503. | Hệ thống bắt ngoại lệ, kích hoạt fallback sang Rule-based Template Generator (tạo câu hỏi phản biện tĩnh dựa trên các Red Flags đã có mà không cần LLM). Tránh làm đơ UI. | ⚠️ Máy chủ AI phản biện đang bảo trì hoặc phản hồi chậm. Hệ thống đã kích hoạt bộ câu hỏi phản biện nguyên tắc chuẩn. |
| `ERR_FAITHFULNESS_BELOW_THRESHOLD` | DeepEval đo lường phát hiện Agent tự bịa ra con số tài chính không có trong JSON đầu vào ($\text{Faithfulness} < 0.95$). | Hệ thống tự động kích hoạt Regenerate với `temperature = 0.0` và kèm lời nhắc nghiêm ngặt: `"You invented numbers. Use ONLY numbers from context"`. Nếu lần 2 vẫn vi phạm, thay thế đoạn vi phạm bằng cảnh báo. | ⚠️ Hệ thống đã tự động lọc bỏ một số nhận định chưa được đối chiếu xác thực từ BCTC gốc. |
| `ERR_DISCLAIMER_VIOLATION` | Agent sơ suất sinh ra câu từ khuyến nghị đầu tư: *"Bạn nên mua/bán cổ phiếu này ngay"*. | Regex Guardrail trong `src/llmops/guardrails.py` phát hiện từ cấm, tự động cắt bỏ và thay thế bằng câu trung lập, ghi log vi phạm nghiêm trọng về Langfuse Alert. | ℹ️ Báo cáo được lọc tự động tuân thủ quy định không đưa ra khuyến nghị mua bán tài chính. |
| `WARN_NO_MACRO_TOOL_DATA` | Tool tra cứu vĩ mô không tìm thấy tin tức mới về ngành hàng hoặc giá cả hàng hóa. | Tác tử Macro trả về `macro_context_evaluation = None`. Supervisor tiếp tục luồng tổng hợp bình thường mà không bị block. | ℹ️ Không ghi nhận biến động vĩ mô bất thường đột biến trong kỳ phân tích. |

### 6. Acceptance Criteria (BDD Tests)

#### Scenario 4.1: Happy Path - Kích hoạt phản biện Socratic thành công trên MWG
```gherkin
Given Người dùng giả định tăng trưởng MWG g = 15%/năm và WACC = 10.0%
And Dữ liệu lịch sử cho thấy 3 năm qua biên lợi nhuận gộp giảm từ 25% xuống 21%
When Người dùng nhấn nút "Challenge My Valuation"
Then Multi-Agent LangGraph hoàn tất thẩm định trong dưới 6.0 giây
And Trả về đúng 3 câu hỏi Socratic chất vấn về tăng trưởng, biên lợi nhuận và chi phí vốn
And Báo cáo chứa đầy đủ Disclaimer pháp lý theo quy chuẩn
And Toàn bộ số liệu trích dẫn trong câu hỏi đều khớp 100% với JSON đầu vào
```

#### Scenario 4.2: Exception - LLM sinh số liệu ảo giác bị Guardrail chặn
```gherkin
Given Tác tử Valuation Challenger sinh câu trả lời có chứa cụm từ "Dự nợ trái phiếu 100.000 tỷ"
And Con số "100.000" hoàn toàn không có trong JSON BCTC của doanh nghiệp
When Hàm verify_numerical_grounding thực thi kiểm tra
Then Hệ thống phát hiện vi phạm ảo giác số học (Hallucination Detected)
And Kích hoạt cơ chế Regenerate hoặc loại bỏ câu văn vi phạm
And Ghi nhận sự kiện cảnh báo lên Langfuse Dashboard
```

#### Scenario 4.3: Alternative Path - Hit Redis Semantic Cache
```gherkin
Given Ticker "HPG" với bộ tham số WACC = 11.5% và g = 8% đã được phân tích trước đó 10 phút
And Dữ liệu đã nằm trong Redis Cache
When Người dùng nhấn "Challenge My Valuation" với cùng bộ tham số
Then Hệ thống không gọi tới OpenAI API (tiết kiệm token)
And Kết quả phản biện được trả về trong thời gian dưới 0.2 giây
```

---

# USE CASE 05: Xuất Báo cáo Đầu tư One-Pager (`Export Investment Memo`)

### 1. Metadata & SLA
- **Use Case ID:** `UC-05`
- **Tên Use Case:** Đóng gói toàn bộ kết quả phân tích định lượng, bảng định giá đa kịch bản và câu hỏi phản biện thành tệp tài liệu One-Pager (Markdown / PDF).
- **Module phụ trách:** `src/ui/report_gen.py`
- **Input Schema:** `FinancialStatementSchema`, `RedFlagReportSchema`, `ValuationOutputSchema`, `AgentCritiqueSchema`
- **Output Schema:** File nhị phân PDF (`application/pdf`) hoặc File văn bản Markdown (`text/markdown`)
- **Cam kết Độ trễ (SLA Latency):** $\le 1.0\text{s}$ cho Markdown export; $\le 2.0\text{s}$ cho PDF rendering kèm font tiếng Việt.

### 2. Pre-conditions & Post-conditions
- **Pre-conditions:**
  - Các bước tính toán định lượng (UC-01, UC-02, UC-03) đã hoàn thành.
  - Phân hệ phản biện Multi-Agent (UC-04) đã hoàn tất hoặc người dùng chọn xuất báo cáo chỉ có phần định lượng.
  - Người dùng bấm nút `Export Investment Memo (PDF/MD)`.
- **Post-conditions:**
  - Tệp báo cáo được tạo ra hoàn chỉnh, định dạng đẹp mắt theo phong cách Investment Memo chuẩn Phố Wall / Quỹ đầu tư giá trị.
  - Trình duyệt tự động kích hoạt tải tệp về máy tính người dùng.

### 3. Main Success Scenario (Luồng chuẩn)
1. **Step 1 (User Action):** Người dùng bấm nút `Export Investment Memo` trên thanh tác vụ của Streamlit Dashboard và chọn định dạng (`PDF` hoặc `Markdown`).
2. **Step 2 (State Aggregation):** `report_gen.py` thu thập toàn bộ dữ liệu từ Session State:
   - Thông tin doanh nghiệp và BCTC 5 năm.
   - Thẻ điểm sức khỏe tài chính & danh sách bẫy kế toán (Red Flags).
   - Bảng định giá 3 kịch bản Bear/Base/Bull và ma trận độ nhạy.
   - Báo cáo phản biện của Hội đồng Đa tác tử (Forensic Notes & Socratic Questions).
3. **Step 3 (Template Rendering):** Hệ thống nạp dữ liệu vào template Jinja2 chuyên nghiệp, chia cấu trúc rõ ràng:
   - *Phần 1:* Executive Summary & Tín hiệu Đèn giao thông rủi ro.
   - *Phần 2:* Phân tích chuyên sâu DuPont 3 bước & Dòng tiền.
   - *Phần 3:* Mô hình Định giá DCF & Ma trận Biên an toàn.
   - *Phần 4:* Biên bản Phản biện Socrate của Hội đồng Thẩm định Độc lập.
   - *Phần 5:* Tuyên bố miễn trừ trách nhiệm pháp lý (Mandatory Disclaimer).
4. **Step 4 (Document Compilation):**
   - Nếu là Markdown: Xuất trực tiếp tệp UTF-8 `.md`.
   - Nếu là PDF: Chuyển đổi HTML/CSS sang PDF qua `WeasyPrint` hoặc `ReportLab`, nhúng font Unicode tiếng Việt (Roboto/Inter) để không bị lỗi ký tự có dấu.
5. **Step 5 (Download Trigger):** Streamlit cung cấp nút `Download Investment Memo` để lưu tệp về máy.

### 6. Alternative Flows
- **AF 5.1 - Export Quantitative-Only Memo:** Người dùng chưa bấm chạy phân hệ Multi-Agent nhưng muốn xuất ngay bảng tính định giá và Red Flags. Hệ thống nhận diện `AgentCritiqueSchema is None`, tự động sinh Memo phần 1, 2, 3 và ghi chú: *"Phiên thẩm định phản biện chưa được kích hoạt."*

### 5. Exception & Financial Edge Cases

| Mã lỗi / Tình huống | Điều kiện kích hoạt | Hành vi xử lý bắt buộc của hệ thống | Thông báo hiển thị UI |
|---|---|---|---|
| `ERR_PREMATURE_EXPORT` | Người dùng bấm nút Export khi chưa nhập mã cổ phiếu hoặc dữ liệu BCTC chưa tải xong. | Vô hiệu hóa nút bấm (Disabled State) trên UI cho tới khi có dữ liệu hợp lệ. Nếu gọi qua API trực tiếp, trả về HTTP 400 `DataNotReady`. | ⚠️ Vui lòng thực hiện phân tích cổ phiếu trước khi xuất báo cáo. |
| `ERR_PDF_FONT_ENCODING` | Trình tạo PDF không tìm thấy font Unicode tiếng Việt dẫn đến lỗi hiển thị ô vuông hoặc dấu hỏi (mojibake). | Cấu hình nhúng font tĩnh chuẩn Google Fonts (`Inter` hoặc `Roboto`) dạng base64/local TTF vào stylesheet của PDF renderer. Fallback về Markdown nếu lỗi engine PDF. | ⚠️ Không thể khởi tạo PDF do lỗi font hệ thống. Hệ thống đã tự động chuyển đổi sang định dạng Markdown. |
| `ERR_LARGE_PAYLOAD_TIMEOUT` | Báo cáo chứa nhiều biểu đồ phức tạp gây timeout quá 5 giây khi render PDF. | Tối ưu hóa kích thước vector chart (chuyển Plotly sang ảnh tĩnh PNG nén 150 DPI trước khi chèn vào PDF). | ⏳ Đang nén biểu đồ và kết xuất tài liệu PDF, vui lòng chờ trong giây lát... |

### 6. Acceptance Criteria (BDD Tests)

#### Scenario 5.1: Happy Path - Xuất thành công One-Pager Investment Memo định dạng PDF
```gherkin
Given Phân tích cổ phiếu "HPG" đã hoàn tất đầy đủ 4 tầng thông tin
When Người dùng nhấn nút "Export Investment Memo (PDF)"
Then Hệ thống sinh tệp PDF trong thời gian dưới 2.0 giây
And Tệp PDF hiển thị hoàn hảo tiếng Việt có dấu, không lỗi font
And Tài liệu chứa đủ 5 phần: Tóm tắt rủi ro, DuPont, Định giá DCF, Phản biện Socrate, và Disclaimer
```

#### Scenario 5.2: Alternative Path - Xuất báo cáo khi chưa kích hoạt Multi-Agent
```gherkin
Given Người dùng mới chỉ thực hiện quét BCTC và định giá DCF (chưa chạy Agent phản biện)
When Người dùng nhấn "Export Markdown Memo"
Then Hệ thống sinh tệp Markdown hoàn chỉnh chứa toàn bộ bảng tính định lượng
And Phần phản biện hiển thị ghi chú: "Phiên thẩm định phản biện chưa được kích hoạt"
And Tệp tải về thành công và hợp lệ cú pháp GitHub Flavored Markdown
```

#### Scenario 5.3: Exception - Cố tình xuất báo cáo khi chưa có dữ liệu phân tích
```gherkin
Given Người dùng vừa mở Dashboard và chưa nhập bất kỳ mã cổ phiếu nào
When Nút Export được kích hoạt
Then Nút bấm ở trạng thái Disabled
And Nếu gửi request trực tiếp tới API, trả về mã lỗi HTTP 400 Bad Request
And Không có tệp rác nào được sinh ra trên hệ thống
```

---

# TỔNG KẾT MA TRẬN PHỤ THUỘC GIỮA CÁC USE CASES

```
┌────────────────────────────────────────────────────────┐
│     UC-01: Ingest & Sanitize Financial Statements      │
└───────────────────────────┬────────────────────────────┘
                            │ (FinancialStatementSchema)
                            ▼
┌────────────────────────────────────────────────────────┐
│    UC-02: Health Check & Rule-based Red Flags Engine   │
└───────────────────────────┬────────────────────────────┘
                            │ (RedFlagReportSchema)
                            ▼
┌────────────────────────────────────────────────────────┐
│    UC-03: Dynamic Valuation & Sensitivity Matrix       │
└───────────────────────────┬────────────────────────────┘
                            │ (ValuationOutputSchema)
                            ▼
┌────────────────────────────────────────────────────────┐
│    UC-04: Socratic Devil's Advocate Multi-Agent        │
└───────────────────────────┬────────────────────────────┘
                            │ (AgentCritiqueSchema)
                            ▼
┌────────────────────────────────────────────────────────┐
│    UC-05: Export One-Pager Investment Memo (PDF/MD)    │
└────────────────────────────────────────────────────────┘
```
Bản đặc tả trên cung cấp nền tảng toàn diện và đóng vai trò kim chỉ nam bất biến cho toàn bộ chu trình kiểm thử tích hợp (Integration Tests) và phát triển mã nguồn của dự án **ValueInvest-Engine**.
