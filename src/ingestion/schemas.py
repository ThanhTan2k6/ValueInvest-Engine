"""
Pydantic v2 Data Contracts for ValueInvest-Engine.
Enforces strict typing, accounting equation validation, and anti-hallucination boundaries.
"""

from typing import List, Dict, Optional, Literal
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator,
    PositiveFloat,
    NonNegativeFloat
)


# =====================================================================
# 1. BCTC DATA SCHEMAS (Thông tư 200/2014/TT-BTC)
# =====================================================================

class BalanceSheetItem(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)

    period: str = Field(..., description="Kỳ báo cáo, e.g., '2023-Q4' hoặc '2023-FY'")
    # Tài sản ngắn hạn (Mã 100)
    cash_and_cash_equivalents: NonNegativeFloat = Field(..., description="Tiền và tương đương tiền (Mã 110)")
    short_term_investments: NonNegativeFloat = Field(0.0, description="Đầu tư tài chính ngắn hạn (Mã 120)")
    short_term_receivables: NonNegativeFloat = Field(..., description="Phải thu ngắn hạn (Mã 130)")
    inventories: NonNegativeFloat = Field(..., description="Hàng tồn kho (Mã 140)")
    other_current_assets: NonNegativeFloat = Field(0.0, description="Tài sản ngắn hạn khác (Mã 150)")
    total_current_assets: NonNegativeFloat = Field(..., description="Tổng tài sản ngắn hạn (Mã 100)")

    # Tài sản dài hạn (Mã 200)
    fixed_assets: NonNegativeFloat = Field(..., description="Tài sản cố định thuần (Mã 220)")
    construction_in_progress: NonNegativeFloat = Field(0.0, description="Chi phí XDCB dở dang (Mã 242)")
    long_term_investments: NonNegativeFloat = Field(0.0, description="Đầu tư tài chính dài hạn (Mã 250)")
    other_long_term_assets: NonNegativeFloat = Field(0.0, description="Tài sản dài hạn khác (Mã 260)")
    total_non_current_assets: NonNegativeFloat = Field(..., description="Tổng tài sản dài hạn (Mã 200)")

    # Tổng tài sản (Mã 270)
    total_assets: NonNegativeFloat = Field(..., description="Tổng cộng tài sản (Mã 270)")

    # Nợ phải trả (Mã 300)
    short_term_borrowings: NonNegativeFloat = Field(..., description="Vay và nợ thuê TC ngắn hạn (Mã 320)")
    short_term_liabilities: NonNegativeFloat = Field(..., description="Nợ ngắn hạn (Mã 310)")
    long_term_borrowings: NonNegativeFloat = Field(0.0, description="Vay và nợ thuê TC dài hạn (Mã 338)")
    total_liabilities: NonNegativeFloat = Field(..., description="Tổng nợ phải trả (Mã 300)")

    # Vốn chủ sở hữu (Mã 400)
    share_capital: NonNegativeFloat = Field(..., description="Vốn góp của chủ sở hữu (Mã 411)")
    retained_earnings: float = Field(..., description="Lợi nhuận sau thuế chưa phân phối (Mã 421) - có thể âm")
    total_equity: float = Field(..., description="Tổng vốn chủ sở hữu (Mã 400) - có thể âm khi lỗ lũy kế vượt vốn")

    # Tổng nguồn vốn (Mã 440)
    total_resources: float = Field(..., description="Tổng cộng nguồn vốn (Mã 440)")

    @model_validator(mode='after')
    def verify_balance_sheet_equation(self) -> 'BalanceSheetItem':
        """Kiểm tra đẳng thức kế toán: Tài sản == Nguồn vốn với sai số < 1e-4."""
        diff = abs(self.total_assets - self.total_resources)
        if diff > 1e-4:
            raise ValueError(
                f"Lỗi cân đối BCTC kỳ {self.period}: Tổng tài sản ({self.total_assets}) "
                f"!= Tổng nguồn vốn ({self.total_resources}). Chênh lệch: {diff}"
            )
        return self


class IncomeStatementItem(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)

    period: str
    gross_revenue: NonNegativeFloat = Field(..., description="Doanh thu bán hàng và CCDV (Mã 01)")
    revenue_deductions: NonNegativeFloat = Field(0.0, description="Các khoản giảm trừ doanh thu (Mã 02)")
    net_revenue: NonNegativeFloat = Field(..., description="Doanh thu thuần (Mã 10)")
    cost_of_goods_sold: NonNegativeFloat = Field(..., description="Giá vốn hàng bán (Mã 11)")
    gross_profit: float = Field(..., description="Lợi nhuận gộp (Mã 20)")
    financial_income: NonNegativeFloat = Field(0.0, description="Doanh thu hoạt động tài chính (Mã 21)")
    interest_expense: NonNegativeFloat = Field(0.0, description="Chi phí lãi vay (Mã 23)")
    financial_expenses: NonNegativeFloat = Field(0.0, description="Chi phí tài chính (Mã 22)")
    selling_expenses: NonNegativeFloat = Field(0.0, description="Chi phí bán hàng (Mã 25)")
    administrative_expenses: NonNegativeFloat = Field(0.0, description="Chi phí QLDN (Mã 26)")
    operating_profit: float = Field(..., description="Lợi nhuận thuần từ HĐKD (Mã 30)")
    net_other_income: float = Field(0.0, description="Lợi nhuận khác (Mã 40)")
    profit_before_tax: float = Field(..., description="Tổng lợi nhuận kế toán trước thuế (Mã 50)")
    current_corporate_tax: NonNegativeFloat = Field(0.0, description="Chi phí thuế TNDN hiện hành (Mã 51)")
    net_profit_after_tax: float = Field(..., description="Lợi nhuận sau thuế của công ty mẹ (Mã 60)")


class CashFlowItem(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)

    period: str
    net_cfo: float = Field(..., description="Lưu chuyển tiền thuần từ HĐ kinh doanh (Mã 20)")
    capex_purchases: float = Field(..., description="Tiền chi để mua sắm, XD TSCĐ (Mã 21) - thường ghi âm")
    net_cfi: float = Field(..., description="Lưu chuyển tiền thuần từ HĐ đầu tư (Mã 30)")
    borrowing_proceeds: NonNegativeFloat = Field(0.0, description="Tiền thu từ đi vay (Mã 33)")
    borrowing_repayments: NonNegativeFloat = Field(0.0, description="Tiền trả nợ gốc vay (Mã 34)")
    net_cff: float = Field(..., description="Lưu chuyển tiền thuần từ HĐ tài chính (Mã 40)")
    net_change_in_cash: float = Field(..., description="Lưu chuyển tiền thuần trong kỳ (Mã 50)")


class FinancialStatementSchema(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)

    ticker: str = Field(..., min_length=3, max_length=5, pattern="^[A-Z]{3,5}$")
    company_name: str
    industry: str
    exchange: Literal["HOSE", "HNX", "UPCOM"]
    currency: Literal["VND"] = "VND"
    unit_multiplier: float = Field(1.0, description="Hệ số nhân (1.0 = VND, 1e9 = Tỷ VND)")
    balance_sheets: List[BalanceSheetItem]
    income_statements: List[IncomeStatementItem]
    cash_flow_statements: List[CashFlowItem]
    notes_extracts: Optional[Dict[str, str]] = Field(default_factory=dict)


# =====================================================================
# 2. RED FLAG & HEALTH CHECK SCHEMAS
# =====================================================================

class SingleRedFlagTrigger(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)

    flag_id: str = Field(..., description="Mã định danh cảnh báo, e.g. 'CRIT_CFO_DIVERGENCE'")
    severity: Literal["CRITICAL", "WARNING", "SAFE"]
    category: Literal["LIQUIDITY", "EARNINGS_QUALITY", "LEVERAGE", "OPERATIONAL_MOAT", "RELATED_PARTY"]
    title: str = Field(..., description="Tiêu đề ngắn gọn của bẫy kế toán")
    metric_value: float = Field(..., description="Giá trị đo lường thực tế")
    threshold_value: float = Field(..., description="Ngưỡng kích hoạt cảnh báo")
    evidence: str = Field(..., description="Mô tả bằng chứng định lượng cụ thể")


class RedFlagReportSchema(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)

    ticker: str
    assessment_period: str
    critical_count: int
    warning_count: int
    safe_count: int
    flags: List[SingleRedFlagTrigger]
    dupont_analysis: Dict[str, Optional[float]]
    interest_coverage_ratio: Optional[float]
    net_debt_to_equity: Optional[float]


# =====================================================================
# 3. VALUATION & DCF SCHEMAS
# =====================================================================

class DCFInputParams(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)

    ticker: str = Field(..., pattern="^[A-Z]{3,5}$")
    current_market_price: PositiveFloat = Field(..., description="Thị giá hiện tại (VND)")
    shares_outstanding: int = Field(..., gt=0, description="Số lượng cổ phiếu lưu hành")
    base_fcf: float = Field(..., description="Dòng tiền tự do FCF kỳ cơ sở (VND)")
    stage1_growth_rate: float = Field(..., ge=-0.5, le=1.0, description="Tăng trưởng FCF Giai đoạn 1 (e.g. 0.08 = 8%)")
    stage1_years: int = Field(5, ge=3, le=10, description="Số năm dự phóng Giai đoạn 1")
    terminal_growth_rate: float = Field(0.025, ge=0.0, le=0.06, description="Tăng trưởng vĩnh viễn (e.g. 0.025 = 2.5%)")
    wacc: float = Field(..., ge=0.05, le=0.30, description="Chi phí vốn bình quân WACC (e.g. 0.11 = 11%)")
    net_debt: float = Field(..., description="Tổng nợ vay chịu lãi trừ Tiền & Tương đương tiền")

    @model_validator(mode='after')
    def validate_wacc_greater_than_terminal_g(self) -> 'DCFInputParams':
        if self.wacc <= self.terminal_growth_rate:
            raise ValueError(
                f"WACC ({self.wacc*100:.2f}%) phải lớn hơn Terminal Growth ({self.terminal_growth_rate*100:.2f}%) "
                f"để thỏa mãn điều kiện hội tụ Gordon Growth Model."
            )
        return self


class ScenarioValuationResult(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)

    scenario_name: Literal["Bear", "Base", "Bull"]
    assumed_stage1_g: float
    assumed_wacc: float
    intrinsic_value_per_share: float
    margin_of_safety: float
    verdict: Literal["DEEP_DISCOUNT", "MODERATE_BUFFER", "FAIR_VALUE", "EXPENSIVE"]


class ValuationOutputSchema(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)

    ticker: str
    current_market_price: float
    enterprise_value: float
    equity_value: float
    intrinsic_value_per_share: float
    margin_of_safety: float
    scenarios: List[ScenarioValuationResult]
    sensitivity_wacc_steps: List[float]
    sensitivity_g_steps: List[float]
    sensitivity_matrix: List[List[Optional[float]]]


# =====================================================================
# 4. MULTI-AGENT CRITIQUE & SYNTHESIS SCHEMAS
# =====================================================================

class SocraticCritiquePoint(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)

    area: Literal["GROWTH", "CAPEX_DEBT", "MARGIN_PRICING", "ACCOUNTING_QUALITY"]
    user_assumption: str = Field(..., description="Giả định user đưa ra")
    counter_evidence: str = Field(..., description="Dữ kiện thực tế phản bác từ BCTC/Thuyết minh")
    socratic_question: str = Field(..., description="Câu hỏi truy vấn sâu buộc user giải trình")
    risk_level: Literal["HIGH", "MEDIUM", "LOW"]


class AgentCritiqueSchema(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)

    ticker: str
    forensic_auditor_summary: str = Field(..., max_length=1500)
    valuation_challenger_points: List[SocraticCritiquePoint]
    macro_context_evaluation: Optional[str] = Field(None, max_length=1000)
    overall_skepticism_rating: Literal["VERY_HIGH", "HIGH", "MODERATE", "LOW"]
    synthesis_memo_markdown: str = Field(..., max_length=3000)
    regulatory_disclaimer: str = Field(
        default=(
            "Báo cáo này được lập cho mục đích cung cấp thông tin và kiểm toán rủi ro độc lập "
            "theo nguyên lý đầu tư giá trị. Đây không phải lời khuyên đầu tư tài chính theo "
            "quy định của Ủy ban Chứng khoán Nhà nước."
        )
    )
