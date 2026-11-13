# Technical Specification 03: Golden Dataset & CI/CD Eval Pipeline (`spec_03_eval_and_golden_dataset.md`)
> **Standard:** DeepEval Metrics, 10 Production HOSE/HNX Golden Test Cases, Strict GitHub Actions Quality Gate

---

## 1. Danh mục 10 Golden Test Cases (HOSE/HNX Accounting Traps)

Bộ dữ liệu này được chuẩn hóa dưới dạng JSON lưu tại `data/golden_eval/cases.json`, bao gồm các ca điển hình về bẫy kế toán và thử thách định giá trên thị trường chứng khoán Việt Nam:

| # | Ticker | Năm BCTC | Loại Bẫy Kế toán Trọng yếu | Chỉ số Kích hoạt (Deterministic Red Flag) | Kỳ vọng Đầu ra của Multi-Agent |
|---|---|---|---|---|---|
| **1** | **NVL** | 2022-FY | Đáo hạn nợ trái phiếu & CFO âm sâu | `Short_Debt_to_Cash = 8.42x`, `CFO = -3,200 tỷ VND` | Cảnh báo tái cấu trúc nợ, đặt câu hỏi về tính thanh khoản dự án Aqua City |
| **2** | **TTF** | 2016-FY | Hàng tồn kho "bốc hơi" bí ẩn | `Inventory_to_Assets = 42%`, Biên LN gộp âm | Bóc tách Thuyết minh về hàng tồn kho thiếu hụt hàng nghìn tỷ sau kiểm toán |
| **3** | **FLC** | 2020-FY | Tạm ứng & Phải thu bên liên quan | `Other_Receivables / Assets > 65%` | Bóc trần dòng tiền lòng vòng sang các công ty con, đối tác sân sau |
| **4** | **ROS** | 2018-FY | Tăng vốn ảo qua ủy thác đầu tư | `Vốn góp tăng 3.000%`, `Ủy thác đầu tư > 80% vốn` | Nhận diện thủ thuật tăng vốn điều lệ không có tiền thực đối ứng |
| **5** | **HPG** | 2022-Q3 | Chu kỳ ngành thép & Nợ dự án DQ2 | `Gross Margin rơi về 2.9%`, `Nợ vay / Vốn CSH > 0.9x` | Thử thách giả định tăng trưởng trong đáy chu kỳ giá nguyên vật liệu |
| **6** | **HNG** | 2021-FY | Lỗ lũy kế âm vốn chủ sở hữu | `Lỗ lũy kế vượt Vốn điều lệ`, `ROE = None` | Cảnh báo Distressed Equity, từ chối định giá P/E truyền thống |
| **7** | **MWG** | 2023-FY | Bão hòa cửa hàng ICT & Giảm biên gộp | `Gross Margin sụt 4 năm liên tiếp`, `DSO tăng` | Chất vấn giả định $g=15\%$ khi đang đóng hàng trăm điểm bán |
| **8** | **VIC** | 2023-FY | Đòn bẩy tài chính & Hỗ trợ xe điện | `Net Debt / EBITDA > 7.0x`, `CapEx tài trợ nợ` | Bóc tách chi phí bảo lãnh và dòng tiền tài trợ cam kết cho VinFast |
| **9** | **CTD** | 2019-FY | Xung đột lợi ích HĐQT & Phải thu khó đòi | `Trích lập dự phòng phải thu tăng 300%` | Phân tích xung đột cổ đông Kusto và dòng tiền tồn đọng tại thầu phụ |
| **10**| **DLG** | 2022-FY | Cho vay nội bộ không tài sản bảo đảm | `Phải thu cho vay cá nhân > 50% vốn` | Chỉ ra nguy cơ mất trắng vốn do không có tài sản bảo đảm khả thi |

---

## 2. Cấu trúc Schema của 1 Golden Test Case (`data/golden_eval/cases.json`)

```json
[
  {
    "case_id": "GOLDEN_01_NVL_2022",
    "ticker": "NVL",
    "company_name": "CTCP Tập đoàn Đầu tư Địa ốc No Va",
    "fiscal_year": "2022",
    "deterministic_context": {
      "revenue": 11151.0,
      "npat": 2181.0,
      "cfo": -3262.0,
      "short_term_debt": 29202.0,
      "cash_and_equivalents": 8600.0,
      "current_ratio": 1.15,
      "quick_ratio": 0.38,
      "red_flags_triggered": [
        "CRIT_CFO_DIVERGENCE",
        "CRIT_REF_CLIFF",
        "WARN_INVENTORY_CONCENTRATION"
      ]
    },
    "extracted_notes_context": {
      "debt_structure": "Dư nợ trái phiếu ngắn hạn đến hạn trả trong 12 tháng là 14.500 tỷ VND.",
      "related_party_advances": "Các khoản tạm ứng và hợp tác phát triển dự án với đối tác liên kết là 18.200 tỷ VND."
    },
    "expected_eval_criteria": {
      "required_mentioned_numbers": ["29202", "8600", "-3262"],
      "forbidden_tokens": ["Khuyến nghị Mua", "Khuyến nghị Bán", "Chốt lời", "Target"],
      "min_faithfulness_score": 0.95,
      "min_hallucination_score": 0.0
    }
  }
]
```

---

## 3. GitHub Actions CI/CD Pipeline Workflow (`.github/workflows/ci.yml`)

Workflow tự động chạy khi có `pull_request` hoặc `push` vào branch `main`. Pipeline sẽ **FAIL và CHẶN MERGE** nếu:
1. `pytest` kiểm thử toán học thất bại hoặc Coverage $< 80\%$.
2. Có bất kỳ file nào trong `src/engine/` hoặc `src/valuation/` import thư viện LLM.
3. Điểm **Faithfulness của DeepEval $< 0.95$** trên 10 Golden Cases.

```yaml
name: ValueInvest-Engine Production CI Quality Gate

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  static-analysis-and-boundaries:
    name: Lint & Architectural Boundary Check
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install Linting Tools
        run: |
          pip install ruff black mypy import-linter

      - name: Verify Architectural Boundaries (No LLM in Math Engine)
        run: |
          echo "Checking boundary: src/engine/ and src/valuation/ must not import LLM packages"
          FORBIDDEN=$(grep -r -E "import langchain|import langgraph|import openai|import instructor|import litellm" src/engine/ src/valuation/ || true)
          if [ -n "$FORBIDDEN" ]; then
            echo "❌ VIOLATION DETECTED: LLM imports found in deterministic engine:"
            echo "$FORBIDDEN"
            exit 1
          fi
          echo "✅ Boundary check passed: Engine is 100% deterministic."

      - name: Run Ruff Linter & MyPy Type Check
        run: |
          ruff check src/ tests/
          mypy src/engine/ src/valuation/ src/ingestion/

  deterministic-math-tests:
    name: Pytest Unit Tests & Math Coverage (> 80%)
    runs-on: ubuntu-latest
    needs: static-analysis-and-boundaries
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install Dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run Pytest with Strict Coverage Enforcement
        run: |
          pytest tests/test_engine_math.py tests/test_red_flags.py \
            --cov=src/engine \
            --cov=src/valuation \
            --cov-report=term-missing \
            --cov-fail-under=80

  llmops-faithfulness-evals:
    name: DeepEval Faithfulness & Anti-Hallucination Gate (Score >= 0.95)
    runs-on: ubuntu-latest
    needs: deterministic-math-tests
    env:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      LANGFUSE_PUBLIC_KEY: ${{ secrets.LANGFUSE_PUBLIC_KEY }}
      LANGFUSE_SECRET_KEY: ${{ secrets.LANGFUSE_SECRET_KEY }}
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install Eval Dependencies
        run: |
          pip install -r requirements.txt
          pip install deepeval

      - name: Run DeepEval on Golden Dataset
        run: |
          python -m pytest tests/test_llm_faithfulness.py -v -s
```
