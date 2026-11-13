# Canonical Accounting Mapping: Circular 200/2014/TT-BTC (`docs/accounting_mapping_tt200.md`)
> **Project:** ValueInvest-Engine  
> **Standard:** Vietnamese Accounting Standards (VAS) - Circular 200/2014/TT-BTC  
> **Target Schema:** `src/ingestion/schemas.py` (`BalanceSheetItem`, `IncomeStatementItem`, `CashFlowItem`)

Tài liệu này định nghĩa bảng ánh xạ chuẩn (Canonical Mapping) giữa các chỉ tiêu và mã số kế toán chính thức theo Thông tư 200/2014/TT-BTC của Bộ Tài chính với các trường dữ liệu tiếng Anh trong Pydantic schema. Module `src/ingestion/sanitizer.py` căn cứ vào bảng này để chuẩn hóa dữ liệu từ các nhà cung cấp (vnstock, Vietstock, FiinGroup, FireAnt, file Excel nội bộ).

---

## 1. Bảng Cân đối Kế toán (Balance Sheet - Mẫu B01-DN)

### Đẳng thức kiểm định kế toán bắt buộc:
$$\text{Mã 270 (Tổng cộng tài sản)} = \text{Mã 440 (Tổng cộng nguồn vốn)}$$
$$\text{Mã 100 (Tài sản ngắn hạn)} + \text{Mã 200 (Tài sản dài hạn)} = \text{Mã 300 (Nợ phải trả)} + \text{Mã 400 (Vốn chủ sở hữu)}$$

| Mã số VAS | Tên chỉ tiêu theo Thông tư 200/2014/TT-BTC | Tên trường Pydantic Schema (`BalanceSheetItem`) | Kiểu dữ liệu | Ràng buộc nghiệp vụ / Ghi chú |
|:---:|:---|:---|:---:|:---|
| **100** | **TÀI SẢN NGẮN HẠN** | `total_current_assets` | `NonNegativeFloat` | $= 110 + 120 + 130 + 140 + 150$ |
| 110 | Tiền và các khoản tương đương tiền | `cash_and_cash_equivalents` | `NonNegativeFloat` | Tiền mặt, tiền gửi ngân hàng, tiền đang chuyển |
| 120 | Đầu tư tài chính ngắn hạn | `short_term_investments` | `NonNegativeFloat` | Tiền gửi có kỳ hạn $\le 12$ tháng, chứng khoán KD |
| 130 | Các khoản phải thu ngắn hạn | `short_term_receivables` | `NonNegativeFloat` | Phải thu khách hàng, trả trước, phải thu khác |
| 131 | *Trong đó: Phải thu ngắn hạn của khách hàng* | `trade_receivables` *(phụ)* | `NonNegativeFloat` | Dùng tính DSO (Kỳ thu tiền bình quân) |
| 136 | *Trong đó: Phải thu ngắn hạn khác* | `other_receivables` *(phụ)* | `NonNegativeFloat` | Quét bẫy tạm ứng / ủy thác đầu tư sân sau |
| 140 | Hàng tồn kho | `inventories` | `NonNegativeFloat` | Đã trừ dự phòng giảm giá hàng tồn kho |
| 150 | Tài sản ngắn hạn khác | `other_current_assets` | `NonNegativeFloat` | Thuế GTGT được khấu trừ, chi phí trả trước NH |
| **200** | **TÀI SẢN DÀI HẠN** | `total_non_current_assets` | `NonNegativeFloat` | $= 210 + 220 + 240 + 250 + 260$ |
| 220 | Tài sản cố định thuần | `fixed_assets` | `NonNegativeFloat` | Nguyên giá trừ Khấu hao lũy kế (Mã 221 - 223) |
| 242 | Chi phí xây dựng cơ bản dở dang | `construction_in_progress` | `NonNegativeFloat` | Dự án nhà máy/công trình chưa nghiệm thu |
| 250 | Đầu tư tài chính dài hạn | `long_term_investments` | `NonNegativeFloat` | Đầu tư công ty con, công ty liên kết |
| 260 | Tài sản dài hạn khác | `other_long_term_assets` | `NonNegativeFloat` | Chi phí trả trước dài hạn, lợi thế thương mại |
| **270** | **TỔNG CỘNG TÀI SẢN** | `total_assets` | `NonNegativeFloat` | **Code 270 = Code 100 + Code 200** |
| **300** | **NỢ PHẢI TRẢ** | `total_liabilities` | `NonNegativeFloat` | $= 310 + 330$ |
| 310 | Nợ ngắn hạn | `short_term_liabilities` | `NonNegativeFloat` | Nợ phải trả trong vòng 1 năm |
| 320 | *Trong đó: Vay và nợ thuê tài chính ngắn hạn* | `short_term_borrowings` | `NonNegativeFloat` | Vay ngân hàng, trái phiếu ngắn hạn chịu lãi |
| 330 | Nợ dài hạn | `long_term_liabilities` *(phụ)* | `NonNegativeFloat` | Nợ phải trả trên 1 năm |
| 338 | *Trong đó: Vay và nợ thuê tài chính dài hạn* | `long_term_borrowings` | `NonNegativeFloat` | Vay dài hạn, trái phiếu dài hạn chịu lãi |
| **400** | **VỐN CHỦ SỞ HỮU** | `total_equity` | `float` | Có thể âm nếu lỗ lũy kế vượt vốn điều lệ |
| 411 | Vốn góp của chủ sở hữu | `share_capital` | `NonNegativeFloat` | Vốn điều lệ thực góp |
| 421 | Lợi nhuận sau thuế chưa phân phối | `retained_earnings` | `float` | Lũy kế lợi nhuận giữ lại (mang dấu âm khi lỗ) |
| **440** | **TỔNG CỘNG NGUỒN VỐN** | `total_resources` | `float` | **Code 440 = Code 300 + Code 400** |

---

## 2. Báo cáo Kết quả Hoạt động Kinh doanh (Income Statement - Mẫu B02-DN)

### Đẳng thức kiểm định kết quả kinh doanh:
$$\text{Mã 10} = \text{Mã 01} - \text{Mã 02}$$
$$\text{Mã 20} = \text{Mã 10} - \text{Mã 11}$$
$$\text{Mã 30} = \text{Mã 20} + \text{Mã 21} - \text{Mã 22} - \text{Mã 25} - \text{Mã 26}$$
$$\text{Mã 50} = \text{Mã 30} + \text{Mã 40}$$
$$\text{Mã 60} = \text{Mã 50} - \text{Mã 51} - \text{Mã 52}$$

| Mã số VAS | Tên chỉ tiêu theo Thông tư 200/2014/TT-BTC | Tên trường Pydantic Schema (`IncomeStatementItem`) | Kiểu dữ liệu | Ý nghĩa trong Phân tích Định lượng |
|:---:|:---|:---|:---:|:---|
| 01 | Doanh thu bán hàng và cung cấp dịch vụ | `gross_revenue` | `NonNegativeFloat` | Doanh thu gộp |
| 02 | Các khoản giảm trừ doanh thu | `revenue_deductions` | `NonNegativeFloat` | Chiết khấu TM, hàng bán bị trả lại, giảm giá |
| **10** | **Doanh thu thuần về bán hàng và CCDV** | `net_revenue` | `NonNegativeFloat` | Doanh thu tính toán chính trong DuPont & Valuation |
| 11 | Giá vốn hàng bán | `cost_of_goods_sold` | `NonNegativeFloat` | Chi phí sản xuất, giá vốn sản phẩm |
| **20** | **Lợi nhuận gộp về bán hàng và CCDV** | `gross_profit` | `float` | Dùng tính Gross Profit Margin ($\text{Mã 20} / \text{Mã 10}$) |
| 21 | Doanh thu hoạt động tài chính | `financial_income` | `NonNegativeFloat` | Lãi tiền gửi, cổ tức, chênh lệch tỷ giá |
| 22 | Chi phí tài chính | `financial_expenses` | `NonNegativeFloat` | Chi phí tài chính tổng thể |
| 23 | *Trong đó: Chi phí lãi vay* | `interest_expense` | `NonNegativeFloat` | Dùng tính Interest Coverage và FCFF |
| 25 | Chi phí bán hàng | `selling_expenses` | `NonNegativeFloat` | Chi phí vận chuyển, hoa hồng, marketing |
| 26 | Chi phí quản lý doanh nghiệp | `administrative_expenses` | `NonNegativeFloat` | Lương bộ máy quản lý, khấu hao văn phòng |
| **30** | **Lợi nhuận thuần từ hoạt động kinh doanh** | `operating_profit` | `float` | Cơ sở tính EBIT ($\text{Mã 30} + \text{Mã 23}$) |
| 40 | Lợi nhuận khác | `net_other_income` | `float` | Thu nhập khác (Mã 31) - Chi phí khác (Mã 32) |
| **50** | **Tổng lợi nhuận kế toán trước thuế** | `profit_before_tax` | `float` | EBT (Earnings Before Tax) |
| 51 | Chi phí thuế TNDN hiện hành | `current_corporate_tax` | `NonNegativeFloat` | Dùng tính thuế suất thực tế ($T_c = \text{Mã 51} / \text{Mã 50}$) |
| **60** | **Lợi nhuận sau thuế thu nhập doanh nghiệp** | `net_profit_after_tax` | `float` | NPAT / Net Income dùng tính ROE, EPS |

---

## 3. Báo cáo Lưu chuyển Tiền tệ (Cash Flow Statement - Mẫu B03-DN Gián tiếp)

### Đẳng thức kiểm định lưu chuyển tiền tệ:
$$\text{Mã 50 (Lưu chuyển tiền thuần trong kỳ)} = \text{Mã 20 (CFO)} + \text{Mã 30 (CFI)} + \text{Mã 40 (CFF)}$$
$$\text{Mã 70 (Tiền và TĐ tiền cuối kỳ)} = \text{Mã 60 (Tiền đầu kỳ)} + \text{Mã 50} + \text{Ảnh hưởng tỷ giá (Mã 61)}$$

| Mã số VAS | Tên chỉ tiêu theo Thông tư 200/2014/TT-BTC | Tên trường Pydantic Schema (`CashFlowItem`) | Kiểu dữ liệu | Ý nghĩa trong Định giá & Red Flags |
|:---:|:---|:---|:---:|:---|
| **20** | **Lưu chuyển tiền thuần từ hoạt động kinh doanh** | `net_cfo` | `float` | **CFO:** Đối chiếu với NPAT quét bẫy lợi nhuận giấy |
| 21 | Tiền chi để mua sắm, xây dựng TSCĐ và TSDH | `capex_purchases` | `float` | **CapEx:** Mang dấu âm trên BCTC, lấy $|Mã\ 21|$ khi tính FCFF |
| **30** | **Lưu chuyển tiền thuần từ hoạt động đầu tư** | `net_cfi` | `float` | **CFI:** Hoạt động đầu tư tài sản, công ty con |
| 33 | Tiền thu từ đi vay | `borrowing_proceeds` | `NonNegativeFloat` | Vốn vay mới huy động |
| 34 | Tiền trả nợ gốc vay | `borrowing_repayments` | `NonNegativeFloat` | Trả nợ gốc vay ngân hàng/trái phiếu |
| **40** | **Lưu chuyển tiền thuần từ hoạt động tài chính** | `net_cff` | `float` | **CFF:** Lưu chuyển tiền hoạt động tài chính |
| **50** | **Lưu chuyển tiền thuần trong kỳ** | `net_change_in_cash` | `float` | $= \text{Mã 20} + \text{Mã 30} + \text{Mã 40}$ |

---

## 4. Công thức Dẫn xuất Chuẩn hóa trong `src/engine/`

| Chỉ tiêu Tài chính Dẫn xuất | Ký hiệu | Công thức tính từ Mã số VAS Thông tư 200 | Xử lý Ngoại lệ |
|:---|:---:|:---|:---|
| **Free Cash Flow to Firm** | $FCFF$ | $\text{Mã 20 (CFO)} + \text{Mã 23 (Lãi vay)} \times (1 - T_c) - |\text{Mã 21 (CapEx)}|$ | Nếu thiếu Mã 23, dùng $FCFF \approx CFO - |CapEx|$ |
| **Net Debt** | $Net\ Debt$ | $(\text{Mã 320} + \text{Mã 338}) - (\text{Mã 110} + \text{Mã 120})$ | Nếu $< 0$ thì $Net\ Debt = 0$ (Doanh nghiệp có tiền ròng) |
| **Interest Coverage** | $ICR$ | $\frac{\text{Mã 30} + \text{Mã 23}}{\text{Mã 23}}$ | Nếu $\text{Mã 23} = 0 \to ICR = 999.0$ (Safe) |
| **Net Profit Margin** | $NPM$ | $\frac{\text{Mã 60}}{\text{Mã 10}}$ | Nếu $\text{Mã 10} \le 0 \to NPM = 0.0$ |
| **Gross Profit Margin** | $GPM$ | $\frac{\text{Mã 20}}{\text{Mã 10}}$ | Nếu suy giảm 3 kỳ liên tiếp $\to$ Bật Warning Flag |
| **Financial Leverage** | $FL$ | $\frac{\text{Mã 270 (Bình quân)}}{\text{Mã 400 (Bình quân)}}$ | Nếu $\text{Mã 400} \le 0 \to FL = None$, bật Critical Flag |
