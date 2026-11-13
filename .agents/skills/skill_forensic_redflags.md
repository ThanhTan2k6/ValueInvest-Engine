---
name: forensic-redflags-audit
description: Guide for quantitative detection of accounting manipulation, creative accounting traps, and extraction of high-risk context from Financial Statement Notes (Thuyết minh BCTC) under Vietnamese Accounting Standards.
---

# Forensic Accounting & Red Flags Detection Skill Guide (`skill_forensic_redflags.md`)

## 1. Triết lý Kiểm toán Rủi ro (Forensic Accounting Philosophy)
Doanh nghiệp có thể "làm đẹp" Báo cáo Kết quả Kinh doanh (P&L) thông qua các thủ thuật kế toán dồn tích (Accrual Accounting), nhưng rất khó che giấu trên Báo cáo Lưu chuyển Tiền tệ (Cash Flow Statement) và Thuyết minh BCTC (Notes). 

Hệ thống phân cấp các dấu hiệu bất thường theo chuẩn đèn giao thông (**Traffic Light System**):
- 🔴 **CRITICAL (Nguy cơ thao túng hoặc vỡ nợ nghiêm trọng)**: Báo động đỏ, yêu cầu giảm trừ giá trị định giá hoặc từ chối mô hình định giá tiêu chuẩn.
- 🟡 **WARNING (Cảnh báo suy giảm chất lượng tài sản & lợi thế cạnh tranh)**: Cần chất vấn sâu và đưa vào kịch bản Bear-case.
- 🟢 **SAFE (Chỉ số lành mạnh)**: Vượt qua các bộ lọc phòng vệ cơ bản.

---

## 2. Bộ Quy tắc Định lượng Hóa Bẫy Kế toán (Quantitative Trap Rules)

### 🔴 CRITICAL FLAGS (Báo động Đỏ)

#### 1. Lợi nhuận Giấy (Paper Profits Divergence):
- **Điều kiện**: Lợi nhuận sau thuế ($NPAT$) dương và tăng trưởng liên tiếp $N \ge 2$ kỳ, nhưng Dòng tiền thuần từ hoạt động kinh doanh ($CFO$) âm kéo dài:
  $$NPAT_t > 0 \quad \text{và} \quad CFO_t < 0 \quad \text{trong 2 năm liên tiếp trở lên}$$
- **Ý nghĩa kế toán**: Doanh nghiệp ghi nhận doanh thu nhưng chưa thu được tiền thực (phải thu ảo), hoặc phải tài trợ hàng tồn kho đọng vốn lớn. Đây là dấu hiệu cổ điển của gian lận doanh thu trước khi sụp đổ thanh khoản.

#### 2. Rủi ro Đáo hạn Thanh khoản (Refinancing Cliff):
- **Điều kiện**: Nợ vay ngắn hạn chịu lãi ($Short\text{-}term\ Debt$, Mã 320) vượt quá tổng Tiền & Tương đương tiền + Đầu tư tài chính ngắn hạn ($Cash\ \&\ Equivalents$, Mã 110 + Mã 120), đồng thời Hệ số Khả năng Thanh toán Hiện hành ($Current\ Ratio < 1.0$):
  $$Short\text{-}term\ Debt > (Cash + ST\ Investments) \times 1.5 \quad \text{và} \quad \frac{Current\ Assets}{Current\ Liabilities} < 1.0$$
- **Ý nghĩa kế toán**: Doanh nghiệp lấy vốn ngắn hạn tài trợ tài sản dài hạn (lệch kỳ hạn tài trợ), phụ thuộc 100% vào việc đảo nợ ngân hàng.

#### 3. Chuyển tiền ra ngoài qua Phải thu khác / Tạm ứng (Related Party Fund Siphoning):
- **Điều kiện**: Chỉ tiêu "Phải thu ngắn hạn khác" (Mã 136) hoặc "Tạm ứng" tăng trưởng gấp 2 lần tốc độ tăng trưởng doanh thu trong 4 quý:
  $$\frac{\Delta Other\ Receivables}{Other\ Receivables_{t-1}} > 2.0 \times \frac{\Delta Revenue}{Revenue_{t-1}} \quad \text{và} \quad Other\ Receivables > 0.15 \times Total\ Assets$$
- **Ý nghĩa kế toán**: Doanh nghiệp rút ruột tiền mặt chuyển cho các công ty con, đối tác sân sau dưới dạng ủy thác đầu tư, tạm ứng dự án không có tài sản bảo đảm.

---

### 🟡 WARNING FLAGS (Cảnh báo Vàng)

#### 1. Đột biến Tỷ lệ Phải thu trên Doanh thu (DSO Expansion):
- **Điều kiện**: Tỷ lệ Phải thu khách hàng / Doanh thu tăng $> 50\%$ so với mức trung bình 3 năm:
  $$\frac{Receivables_t}{Revenue_t} > 1.5 \times \text{Avg}\left(\frac{Receivables_{t-k}}{Revenue_{t-k}}\right)$$
- **Ý nghĩa**: Bán hàng lỏng tay, nới lỏng chính sách tín dụng cho khách hàng để đạt chỉ tiêu doanh thu, hoặc xuất khống hóa đơn.

#### 2. Xói mòn Biên Lợi nhuận Gộp (Moat Deterioration):
- **Điều kiện**: Gross Profit Margin suy giảm liên tiếp trong 3 năm tài chính:
  $$Gross\ Margin_t < Gross\ Margin_{t-1} < Gross\ Margin_{t-2}$$
- **Ý nghĩa**: Doanh nghiệp mất khả năng định giá (Lack of Pricing Power), chi phí đầu vào tăng mà không thể chuyển tiếp cho khách hàng.

#### 3. Vòng quay Hàng tồn kho Chậm lại (Inventory Bloat):
- **Điều kiện**: Ngày tồn kho bình quân ($Days\ Sales\ of\ Inventory - DSI$) tăng trên 40% trong khi tăng trưởng doanh thu chững lại:
  $$DSI = \frac{Average\ Inventory}{COGS} \times 365$$
- **Ý nghĩa**: Hàng hóa ế ẩm, nguy cơ trích lập dự phòng giảm giá hàng tồn kho lớn trong các quý tiếp theo.

---

### 🟢 SAFE CHECKS (Vùng An toàn)
1. **Interest Coverage Ratio**: $\frac{EBIT}{Interest\ Expense} \ge 5.0x$ (hoặc không vay nợ).
2. **Net Debt to Equity**: $\frac{Total\ Debt - Cash}{Equity} \le 0.5x$.
3. **CFO / NPAT Quality Ratio**: $\frac{CFO}{NPAT} \ge 1.0$ (chất lượng lợi nhuận bằng tiền mặt cao).

---

## 3. Quy trình Trích xuất Ngữ cảnh từ Thuyết minh BCTC (Notes Extraction)

LLM không cần đọc toàn bộ 80 trang Thuyết minh. Pipeline chỉ lọc đúng các mục trọng yếu sau để đưa vào prompt của **Forensic Auditor Agent**:

```
[BỘ LỌC CÁC MỤC TRỌNG YẾU THUYẾT MINH BCTC - THÔNG TƯ 200]
├── Mục 5: Tiền và các khoản tương đương tiền (Chi tiết tiền gửi kỳ hạn, tiền bị phong tỏa/thế chấp)
├── Mục 7: Phải thu ngắn hạn / Phải thu khác (Danh sách top 5 đối tác nợ lớn nhất & Trích lập dự phòng khó đòi)
├── Mục 9: Hàng tồn kho (Chi tiết chi phí sản xuất kinh doanh dở dang tại các dự án bất động sản/nhà máy)
├── Mục 15: Chi phí xây dựng cơ bản dở dang (Tiến độ xây dựng, chi phí vốn hóa lãi vay vào dự án)
├── Mục 20: Vay và nợ thuê tài chính (Chi tiết ngân hàng cho vay, lãi suất thả nổi, tài sản thế chấp, lịch trả nợ gốc)
└── Mục 38 / 39: Giao dịch với các bên liên quan (Mua bán hàng hóa, cho vay, bảo lãnh cho Ban Giám đốc & cty liên kết)
```

### Tiêu chuẩn cấu trúc hóa Context cho Forensic Agent:
```json
{
  "ticker": "NVL",
  "period": "2023-FY",
  "quantitative_triggers": [
    {
      "code": "CRIT_REF_CLIFF",
      "level": "CRITICAL",
      "metric": "Short_Debt_to_Cash",
      "value": 8.42,
      "threshold": 1.5,
      "message": "Nợ vay ngắn hạn gấp 8.42 lần lượng tiền mặt và tiền gửi."
    }
  ],
  "extracted_notes": {
    "debt_breakdown": "Tổng nợ ngắn hạn đến hạn 29.500 tỷ. Bao gồm 12.000 tỷ trái phiếu phát hành bởi công ty con với lãi suất 12-14%/năm, tài sản bảo đảm là cổ phần và dự án Aqua City.",
    "related_party_transactions": "Dư nợ cho vay và tạm ứng công ty liên kết lên tới 14.200 tỷ VND, không có tài sản bảo đảm.",
    "contingent_liabilities": "Cam kết bảo lãnh nghĩa vụ nợ cho các công ty đối tác trị giá 8.900 tỷ VND."
  }
}
```
Khi nhận JSON này, Forensic Auditor Agent sẽ đối chiếu trực tiếp giữa số liệu định lượng và thuyết minh để đưa ra các chất vấn chính xác tới từng dòng nợ, từng ngân hàng và từng tài sản thế chấp.
