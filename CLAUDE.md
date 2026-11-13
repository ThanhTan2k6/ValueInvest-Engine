# ValueInvest-Engine Project Governance & Coding Rules

This repository enforces strict **Spec-Driven Development** with a **Decoupled Architecture** separating deterministic financial calculations from probabilistic multi-agent reasoning.

## Core Mandates

### 1. Architectural Boundaries (Zero Math Hallucination)
- **Zero LLM Arithmetic**: LLMs are prohibited from computing ROE, ROIC, WACC, FCFF, DCF, Intrinsic Value, Margin of Safety, or any other numeric financial formula.
- **Strict Isolation**: `src/engine/` and `src/valuation/` MUST NEVER import any LLM or AI packages (`langchain`, `langgraph`, `openai`, `google.genai`, `instructor`, etc.).
- **Unidirectional Data Flow**: Ingestion -> Sanitizer -> Deterministic Math Engine -> Structured JSON Context -> Multi-Agent AI (LangGraph) -> Pydantic Output Guardrails -> Presentation Layer.

### 2. Accounting Integrity (VAS - Circular 200/2014/TT-BTC)
- **Balance Sheet Equality**: Ingested data MUST verify `Assets == Liabilities + Equity` with tolerance `< 1e-4`. Any failure throws `AccountingBalanceError`.
- **VAS Standardization**: Code 270 (Total Assets) must match Code 440 (Total Resources). Revenue and cash flow statements must comply with standard line codes.

### 3. Type Safety & Validation
- **Python 3.11+** required with 100% type annotations.
- **Pydantic v2**: All inter-service boundaries enforce immutable data contracts (`frozen=True, strict=True`).

### 4. Financial Guardrails & Edge Cases
- **Division by Zero**: Handled deterministically (e.g., Interest Expense = 0 -> Interest Coverage = `float('inf')` with sentinel handling).
- **Negative Equity**: Flag `DistressedEquityWarning` rather than computing nonsensical leverage ratios.
- **Regulatory Ban on Financial Advice**: Output filters strictly reject direct buy/sell recommendations ("Khuyến nghị Mua/Bán", "Target price cam kết").

### 5. Performance & Testing Targets
- Pytest coverage > 80% for `src/engine/` and `src/valuation/`.
- Math Engine execution time < 2.0s for 5 years of financial statements.
- Multi-Agent workflow < 6.0s (cold) and < 0.2s (Redis semantic cache hit).
- Faithfulness metric >= 0.95 measured by DeepEval.
