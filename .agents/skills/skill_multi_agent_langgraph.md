---
name: multi-agent-langgraph-orchestration
description: Production blueprint for building the LangGraph StateGraph workflow (Supervisor -> Parallel Forensic, Challenger, Macro Agents -> Synthesis) with Socratic Devil's Advocate reasoning and Instructor/Pydantic structured output.
---

# Multi-Agent LangGraph Orchestration Skill Guide (`skill_multi_agent_langgraph.md`)

## 1. Kiến trúc Đa Tác tử (Multi-Agent StateGraph Architecture)

```
                            ┌────────────────────────┐
                            │    [State: START]      │
                            └───────────┬────────────┘
                                        │
                                        ▼
                            ┌────────────────────────┐
                            │    Supervisor Agent    │
                            │  (Phân tích Input,     │
                            │   Lập kế hoạch audit)  │
                            └───────────┬────────────┘
                                        │
                 ┌──────────────────────┼──────────────────────┐
                 │ (Parallel Execution) │                      │
                 ▼                      ▼                      ▼
      ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
      │  Forensic Auditor  │ │Valuation Challenger│ │   Macro Research   │
      │       Agent        │ │       Agent        │ │     Tool Agent     │
      │(Thuyết minh BCTC,  │ │(Socratic Devil's   │ │(Lãi suất, chu kỳ   │
      │ nợ tiềm tàng, bên  │ │ Advocate, bẻ gãy   │ │ hàng hóa, rủi ro   │
      │ liên quan)         │ │ giả định WACC & g) │ │ vĩ mô ngành)       │
      └──────────┬─────────┘ └──────────┬─────────┘ └──────────┬─────────┘
                 │                      │                      │
                 └──────────────────────┼──────────────────────┘
                                        │ (State Reducer: merge critiques)
                                        ▼
                            ┌────────────────────────┐
                            │   Synthesis Agent      │
                            │ (Kiểm duyệt Guardrail, │
                            │  biên soạn One-Pager)  │
                            └───────────┬────────────┘
                                        │
                                        ▼
                            ┌────────────────────────┐
                            │     [State: END]       │
                            └────────────────────────┘
```

---

## 2. Định nghĩa LangGraph State (`AgentState`)

```python
from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator
from pydantic import BaseModel, Field

class AgentState(TypedDict):
    ticker: str
    company_name: str
    financial_ratios: Dict[str, Any]      # From Deterministic Engine (DuPont, Coverage, Solvency)
    red_flag_triggers: List[Dict[str, Any]]# From Rule-based Red Flags Engine
    valuation_inputs: Dict[str, Any]      # User sliders: WACC, g, base_fcf, current_price
    valuation_outputs: Dict[str, Any]     # DCF Intrinsic Value, MoS, Sensitivity Matrix Summary
    extracted_notes: Dict[str, str]       # Extracted sections from Notes to Financial Statements
    macro_context: Optional[str]          # Commodity prices, interest rate environment
    
    # Reducers for multi-agent outputs
    forensic_critique: Optional[Dict[str, Any]]
    valuation_critique: Optional[Dict[str, Any]]
    macro_critique: Optional[Dict[str, Any]]
    
    # Final synthesized output
    final_memo_markdown: Optional[str]
    audit_verdict: Optional[str]
    disclaimer: str
    errors: Annotated[List[str], operator.add]
```

---

## 3. Triển khai Kỹ thuật Phản biện Socratic (Socratic Devil's Advocate)
Tác tử **Valuation Challenger** không đơn thuần chỉ ra điểm yếu, mà sử dụng phương pháp đặt câu hỏi thẩm vấn Socrate (Socratic Questioning):
1. **Chất vấn Giả định Cốt lõi (Questioning Core Assumptions)**: Bóc trần sự mâu thuẫn giữa giả định tăng trưởng tương lai ($g$) và năng lực tài chính/thị phần hiện thực.
2. **Đối chiếu với Quy luật Hoàn nguyên về Số bình quân (Mean Reversion)**: Doanh nghiệp không thể duy trì ROE $35\%$ mãi mãi trong môi trường kinh tế cạnh tranh khốc liệt.
3. **Thử tải Stress-Test (Stress Testing)**: Giả định điều gì sẽ xảy ra nếu lãi suất thả nổi tăng 300 điểm cơ bản, hoặc giá nguyên vật liệu đầu vào tăng 20%.

### Ví dụ Luận điểm Socratic:
- *"Bạn đang giả định dòng tiền tự do FCFF tăng trưởng $12\%$/năm trong 5 năm tới. Tuy nhiên, tỷ lệ tái đầu tư (Reinvestment Rate) của công ty trong 3 năm qua chỉ đạt $15\%$, và nhà máy hiện hữu đã hoạt động ở mức $98\%$ công suất. Dựa trên cơ sở vật chất nào mà doanh số có thể tăng mà không cần đợt CapEx quy mô lớn làm xói mòn dòng tiền?"*

---

## 4. Ép Structured Output chuẩn với `Instructor` & Pydantic

Để đảm bảo kết quả từ LLM có thể parse 100% thành đối tượng Python có type safety mà không bao giờ bị lỗi format JSON:

```python
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Literal

class SocraticChallengeQuestion(BaseModel):
    category: Literal["GROWTH_ASSUMPTION", "PROFIT_MARGIN_MOAT", "COST_OF_CAPITAL_WACC", "BALANCE_SHEET_DEBT"]
    assumption_stated: str = Field(description="Giả định của người dùng được đối chiếu (ví dụ: g=10%)")
    historical_fact: str = Field(description="Số liệu lịch sử thực tế từ Deterministic Engine (ví dụ: 3 năm qua g bình quân chỉ đạt 3.2%)")
    challenging_question: str = Field(description="Câu hỏi phản biện Socrate buộc nhà đầu tư phải suy xét lại rủi ro")
    severity: Literal["HIGH", "MEDIUM", "LOW"]

class ValuationChallengerReport(BaseModel):
    ticker: str
    overall_skepticism_score: float = Field(ge=0.0, le=10.0, description="Thang điểm hoài nghi từ 0 (hoàn toàn tin cậy) đến 10 (cực kỳ phi thực tế)")
    vulnerabilities: List[str]
    socratic_questions: List[SocraticChallengeQuestion]
    recommended_stress_test_wacc: float = Field(description="Mức WACC đề xuất khi kiểm tra kịch bản xấu nhất")
    recommended_stress_test_g: float = Field(description="Mức g đề xuất khi kiểm tra kịch bản xấu nhất")

def run_valuation_challenger(client: OpenAI, state: AgentState) -> ValuationChallengerReport:
    # Patch client với instructor để ép kiểu Pydantic v2
    instructor_client = instructor.from_openai(client)
    
    prompt = f"""
    Bạn là Chief Risk Officer & Valuation Challenger.
    Dữ liệu định lượng:
    - Ticker: {state['ticker']}
    - Giả định người dùng: {state['valuation_inputs']}
    - Kết quả định giá Math Engine: {state['valuation_outputs']}
    - Các chỉ số tài chính quá khứ: {state['financial_ratios']}
    
    Hãy phân tích và đưa ra 3 câu hỏi Socratic phản biện sâu sắc nhất.
    """
    
    response = instructor_client.chat.completions.create(
        model="gpt-4o", # hoặc gemini-1.5-pro / claude-3-5-sonnet
        response_model=ValuationChallengerReport,
        max_retries=3,
        messages=[
            {"role": "system", "content": "You are a ruthless Socratic valuation challenger for equity investments."},
            {"role": "user", "content": prompt}
        ]
    )
    return response
```

---

## 5. LangGraph StateGraph Compilation

```python
from langgraph.graph import StateGraph, END

def build_valueinvest_graph() -> StateGraph:
    builder = StateGraph(AgentState)
    
    # 1. Thêm Nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("forensic_auditor", forensic_auditor_node)
    builder.add_node("valuation_challenger", valuation_challenger_node)
    builder.add_node("macro_tool", macro_tool_node)
    builder.add_node("synthesis", synthesis_node)
    
    # 2. Thiết lập Edges (Song song phân tích)
    builder.set_entry_point("supervisor")
    builder.add_edge("supervisor", "forensic_auditor")
    builder.add_edge("supervisor", "valuation_challenger")
    builder.add_edge("supervisor", "macro_tool")
    
    # 3. Hội tụ về Synthesis
    builder.add_edge("forensic_auditor", "synthesis")
    builder.add_edge("valuation_challenger", "synthesis")
    builder.add_edge("macro_tool", "synthesis")
    
    # 4. Kết thúc
    builder.add_edge("synthesis", END)
    
    return builder.compile()
```
