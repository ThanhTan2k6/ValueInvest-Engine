---
name: quant-math-engineering
description: Production guide for implementing deterministic financial models (DuPont 3-step, FCFF/FCFE, WACC/CAPM, Sensitivity Matrix, Margin of Safety) with NumPy/Pandas vectorization and Circular 200/BTC edge cases.
---

# Quantitative Math Engine Skill Guide (`skill_quant_math.md`)

## 1. Mục tiêu & Nguyên tắc Thiết kế
Module `src/engine/` và `src/valuation/` chịu trách nhiệm 100% tính toán số học tài chính. Toàn bộ logic phải:
- Không sử dụng vòng lặp Python chậm khi tính ma trận (sử dụng NumPy broadcasting / Pandas vectorization).
- Tuyệt đối không import thư viện LLM hoặc xử lý chuỗi ngôn ngữ tự nhiên.
- Xử lý triệt để các trường hợp ngoại lệ (Edge Cases) thường gặp trong BCTC Việt Nam.

---

## 2. Công thức Chuẩn & Triển khai Kỹ thuật

### 2.1. DuPont 3-Step Decomposition
$$ROE = \left(\frac{Net\ Income}{Revenue}\right) \times \left(\frac{Revenue}{Average\ Assets}\right) \times \left(\frac{Average\ Assets}{Average\ Equity}\right)$$
Tương đương:
$$ROE = Net\ Profit\ Margin \times Asset\ Turnover \times Financial\ Leverage$$

#### Xử lý Edge Cases Việt Nam:
1. **Average Balance Sheet vs Ending Balance Sheet**:
   - Nếu có kỳ trước $t-1$: Dùng $\bar{A} = \frac{A_t + A_{t-1}}{2}$ và $\bar{E} = \frac{E_t + E_{t-1}}{2}$.
   - Nếu là kỳ đầu tiên: Dùng giá trị cuối kỳ ($A_t, E_t$).
2. **Vốn chủ sở hữu âm ($Equity \le 0$)**:
   - Khi doanh nghiệp lỗ lũy kế vượt vốn điều lệ (ví dụ: HVN, TTF thời kỳ khủng hoảng), $Average\ Equity \le 0$ khiến ROE và Financial Leverage bị đảo dấu toán học (toán học ra số dương nhưng bản chất cực kỳ bi đát).
   - **Xử lý**: Trả về `roe=None`, `financial_leverage=None`, đồng thời bật cờ `is_distressed_equity = True`.

```python
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

def compute_dupont_3step(
    net_income: float,
    revenue: float,
    assets_curr: float,
    assets_prev: Optional[float],
    equity_curr: float,
    equity_prev: Optional[float]
) -> Dict[str, Any]:
    if revenue <= 0:
        return {
            "net_profit_margin": 0.0,
            "asset_turnover": 0.0,
            "financial_leverage": None,
            "roe": None,
            "error_flag": "ZERO_OR_NEGATIVE_REVENUE"
        }
    
    avg_assets = (assets_curr + assets_prev) / 2.0 if (assets_prev is not None and assets_prev > 0) else assets_curr
    avg_equity = (equity_curr + equity_prev) / 2.0 if (equity_prev is not None) else equity_curr
    
    net_profit_margin = net_income / revenue
    asset_turnover = revenue / avg_assets if avg_assets > 0 else 0.0
    
    if avg_equity <= 0:
        return {
            "net_profit_margin": net_profit_margin,
            "asset_turnover": asset_turnover,
            "financial_leverage": None,
            "roe": None,
            "is_distressed_equity": True,
            "warning": "Vốn chủ sở hữu âm hoặc bằng 0, không thể tính đòn bẩy tài chính hợp lệ."
        }
        
    financial_leverage = avg_assets / avg_equity
    roe = net_profit_margin * asset_turnover * financial_leverage
    
    return {
        "net_profit_margin": float(net_profit_margin),
        "asset_turnover": float(asset_turnover),
        "financial_leverage": float(financial_leverage),
        "roe": float(roe),
        "is_distressed_equity": False,
        "warning": None
    }
```

---

### 2.2. Dòng tiền Tự do (FCFF & FCFE)
#### FCFF (Free Cash Flow to Firm):
$$FCFF = EBIT \times (1 - T_c) + D\&A - \Delta NWC - CapEx$$
Hoặc từ Báo cáo Lưu chuyển Tiền tệ gián tiếp (Thông tư 200/BTC):
$$FCFF = CFO + Interest\ Expense \times (1 - T_c) - CapEx$$
Trong đó:
- $CapEx$ (Chi đầu tư tài sản cố định) = Chỉ tiêu "Tiền chi để mua sắm, xây dựng TSCĐ và các TSDH khác" (Mã 21 trên B03-DN). Do chỉ tiêu này mang dấu âm trên BCTC, $CapEx = |Mã\ 21|$.
- $\Delta NWC$ = Thay đổi vốn lưu động hoạt động thuần (Khoản phải thu + Hàng tồn kho - Phải trả người bán hoạt động).

#### FCFE (Free Cash Flow to Equity):
$$FCFE = FCFF - Interest\ Expense \times (1 - T_c) + Net\ Borrowing$$
Trong đó:
- $Net\ Borrowing = Tiền\ thu\ từ\ đi\ vay (Mã\ 33) - Tiền\ trả\ nợ\ gốc\ vay (Mã\ 34)$.

---

### 2.3. WACC chuẩn CAPM tại Thị trường Việt Nam
$$WACC = \left(\frac{E}{V}\right) \times R_e + \left(\frac{D}{V}\right) \times R_d \times (1 - T_c)$$
Trong đó:
- $V = E + D$ (Tổng nguồn vốn thị trường hoặc sổ sách).
- $E$: Vốn hóa thị trường = $Số\ lượng\ CP\ lưu\ hành \times Thị\ giá\ hiện\ hành$.
- $D$: Tổng nợ vay chịu lãi = Vay ngắn hạn (Mã 320) + Vay dài hạn (Mã 338). *Lưu ý: Không cộng các khoản phải trả người bán không chịu lãi vào D*.
- $T_c$: Thuế suất TNDN chuẩn (hiện hành tại Việt Nam là 20.0%, trừ trường hợp ưu đãi thuế).
- Chi phí vốn vay $R_d$: $\frac{Chi\ phí\ lãi\ vay}{Nợ\ vay\ chịu\ lãi\ bình\ quân}$. Nếu không có số liệu chi tiết, áp dụng lãi suất vay thương mại bình quân (ví dụ: 8.5% - 10.5%).
- Chi phí vốn cổ phần $R_e$ theo CAPM:
  $$R_e = R_f + \beta \times (R_m - R_f)$$
  * $R_f$ (Risk-free rate): Lợi suất Trái phiếu Chính phủ Việt Nam kỳ hạn 10 năm (chuẩn tham chiếu: ~2.5% - 3.5%).
  * $R_m - R_f$ (Equity Risk Premium - ERP): Phần bù rủi ro vốn cổ phần thị trường cận biên/mới nổi Việt Nam (chuẩn tham chiếu: 7.0% - 8.5%).
  * $\beta$: Hệ số rủi ro hệ thống điều chỉnh (Blended / Hamada Unlevered Beta).

---

### 2.4. Vectorized 2D Sensitivity Matrix ($WACC$ vs $g$)
Để render tức thời trên Dashboard (< 10ms) mà không bị nghẽn CPU, sử dụng broadcasting 2 chiều của NumPy:

```python
import numpy as np

def compute_sensitivity_matrix(
    base_fcf: float,
    projection_years: int,
    wacc_range: np.ndarray,      # 1D array shape (N,) ví dụ: [0.10, 0.11, 0.12, 0.13, 0.14]
    terminal_g_range: np.ndarray,# 1D array shape (M,) ví dụ: [0.02, 0.025, 0.03, 0.035, 0.04]
    shares_outstanding: int,
    net_debt: float,             # Total Interest-Bearing Debt - Cash & Cash Equivalents
    stage1_growth_rate: float = 0.08
) -> np.ndarray:
    """
    Computes a 2D matrix of Intrinsic Value Per Share using NumPy vectorization.
    Output Shape: (len(wacc_range), len(terminal_g_range))
    """
    # 1. Project Cash Flows for Stage 1 (T năm)
    t = np.arange(1, projection_years + 1)
    projected_fcf = base_fcf * ((1 + stage1_growth_rate) ** t) # shape (projection_years,)
    
    # 2. Reshape for broadcasting
    # WACC: shape (N, 1, 1) để broadcast qua các năm t và g
    W = wacc_range[:, np.newaxis, np.newaxis] # (N, 1, 1)
    G = terminal_g_range[np.newaxis, :, np.newaxis] # (1, M, 1)
    
    # PV of Stage 1 Cash Flows: sum over t (axis=2)
    discount_factors = 1.0 / ((1 + W) ** t) # (N, 1, projection_years)
    pv_stage1 = np.sum(projected_fcf * discount_factors, axis=2) # (N, 1) -> broadcast to (N, M)
    pv_stage1 = np.repeat(pv_stage1, len(terminal_g_range), axis=1) # (N, M)
    
    # Terminal Value: TV = FCF_{T} * (1 + g) / (WACC - g)
    # Lưu ý: Điều kiện ổn định Gordon Growth: WACC > g. Nếu WACC <= g -> Invalid.
    final_fcf = projected_fcf[-1]
    
    W_2d = wacc_range[:, np.newaxis] # (N, 1)
    G_2d = terminal_g_range[np.newaxis, :] # (1, M)
    
    spread = W_2d - G_2d
    # Tránh chia cho 0 hoặc WACC <= g
    valid_mask = spread > 0.005 # Chênh lệch tối thiểu 0.5%
    
    tv = np.where(valid_mask, (final_fcf * (1 + G_2d)) / spread, 0.0)
    pv_tv = tv / ((1 + W_2d) ** projection_years)
    
    enterprise_value = pv_stage1 + pv_tv
    equity_value = enterprise_value - net_debt
    
    intrinsic_value_per_share = np.where(
        valid_mask,
        np.maximum(equity_value / shares_outstanding, 0.0),
        np.nan
    )
    
    return intrinsic_value_per_share
```

---

### 2.5. Margin of Safety (MoS)
$$MoS = \frac{Intrinsic\ Value - Current\ Market\ Price}{Intrinsic\ Value} \times 100\%$$
- **Nếu $Intrinsic\ Value \le 0$**: Trả về `MoS = -100.0%` hoặc `None`, cấm trả về số dương gây hiểu lầm.
- **Tiêu chuẩn Benjamin Graham**:
  * $MoS \ge 30\%$: Hấp dẫn (Undervalued with significant buffer).
  * $10\% \le MoS < 30\%$: Xem xét (Moderate buffer).
  * $0\% \le MoS < 10\%$: Định giá hợp lý (Fair value).
  * $MoS < 0\%$: Đắt (Overvalued).
