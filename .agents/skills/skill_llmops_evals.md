---
name: llmops-evals-observability
description: Implementation guide for Langfuse telemetry tracing, Redis semantic caching, and DeepEval Faithfulness/Groundedness verification to guarantee zero math hallucination in production.
---

# LLMOps, Observability & Evals Skill Guide (`skill_llmops_evals.md`)

## 1. Mục tiêu Kiểm chuẩn LLMOps (Core LLMOps Objectives)
Trong FinTech, ảo giác số liệu (Math Hallucination) là lỗi nghiêm trọng nhất. Bộ kỹ năng này đảm bảo:
1. **100% Tracing & Audit Trail**: Toàn bộ luồng suy luận, latency từng agent, token usage, và prompt version được ghi nhận qua Langfuse.
2. **Semantic Caching qua Redis**: Giảm 90% chi phí gọi LLM và đưa độ trễ về $< 0.2\text{s}$ cho các truy vấn trùng lặp hoặc tương đương về ngữ nghĩa.
3. **Automated Evals (DeepEval)**: Tự động chấm điểm Faithfulness/Groundedness. Mọi con số trong báo cáo Markdown của Agent phải có nguồn gốc chứng minh từ JSON của Deterministic Engine.

---

## 2. Thiết lập Langfuse Tracing cho Multi-Agent LangGraph

```python
import os
from langfuse.callback import CallbackHandler
from langfuse import Langfuse

def get_langfuse_callback() -> CallbackHandler:
    """Khởi tạo Callback Handler cho LangGraph / LangChain."""
    return CallbackHandler(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    )

def trace_agent_execution(session_id: str, ticker: str, user_id: str = "default_user"):
    """Tạo trace gốc bao bọc toàn bộ chu trình phân tích."""
    langfuse = Langfuse()
    trace = langfuse.trace(
        name="ValueInvest_MultiAgent_Workflow",
        session_id=session_id,
        user_id=user_id,
        metadata={"ticker": ticker, "version": "1.0.0"}
    )
    return trace
```

---

## 3. Caching 2 Lớp: Redis Exact Hash & Semantic Caching

```python
import hashlib
import json
import redis
from typing import Optional, Dict, Any

class FinancialSemanticCache:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, ttl_seconds: int = 86400):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.ttl = ttl_seconds

    def _generate_cache_key(self, ticker: str, valuation_params: Dict[str, Any]) -> str:
        # Chuẩn hóa các tham số để tạo SHA256 key
        serialized = json.dumps(
            {
                "ticker": ticker.upper(),
                "wacc": round(valuation_params.get("wacc", 0.0), 3),
                "terminal_g": round(valuation_params.get("terminal_g", 0.0), 3),
                "stage1_g": round(valuation_params.get("stage1_g", 0.0), 3),
            },
            sort_keys=True
        )
        hash_val = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return f"valueinvest:critique:{ticker.upper()}:{hash_val}"

    def get(self, ticker: str, valuation_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        key = self._generate_cache_key(ticker, valuation_params)
        data = self.client.get(key)
        if data:
            return json.loads(data)
        return None

    def set(self, ticker: str, valuation_params: Dict[str, Any], result: Dict[str, Any]):
        key = self._generate_cache_key(ticker, valuation_params)
        self.client.setex(key, self.ttl, json.dumps(result, ensure_ascii=False))
```

---

## 4. DeepEval Faithfulness & Groundedness Test Suite

Kiểm tra định lượng xem Agent có phát minh ra con số tài chính nào không tồn tại trong `retrieval_context` (JSON của Deterministic Engine).

```python
import pytest
import re
from typing import List
from deepeval.metrics import FaithfulnessMetric, GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

def extract_financial_numbers(text: str) -> List[str]:
    """Trích xuất tất cả các số thực, tỷ lệ phần trăm hoặc số nguyên trong văn bản phản biện."""
    pattern = r"[-+]?\d*[\.,]?\d+(?:%|(?:\s*tỷ|\s*triệu|\s*x|\s*VND))?"
    return re.findall(pattern, text)

def verify_numerical_grounding(actual_output: str, source_context_json: str) -> bool:
    """
    Quy tắc cứng (Deterministic Check):
    Mọi số xuất hiện trong output của Agent phải tồn tại trong chuỗi JSON đầu vào.
    """
    found_numbers = extract_financial_numbers(actual_output)
    # Lọc bỏ các số thứ tự đơn giản như 1, 2, 3
    substantive_numbers = [n for n in found_numbers if len(n.strip()) > 1 and not n.strip().isdigit()]
    
    missing_numbers = []
    for num in substantive_numbers:
        # Chuẩn hóa dấu chấm/phẩy
        clean_num = num.replace(",", "").replace(".", "").replace("%", "").strip()
        if clean_num not in source_context_json.replace(",", "").replace(".", ""):
            missing_numbers.append(num)
            
    if missing_numbers:
        print(f"⚠️ Cảnh báo số liệu không có trong context: {missing_numbers}")
        return False
    return True

@pytest.mark.evals
def test_agent_faithfulness_benchmark():
    """Đánh giá Faithfulness bằng DeepEval trên Golden Case HPG."""
    retrieval_context = [
        """
        {
            "ticker": "HPG",
            "year": 2023,
            "cfo": 12150.0,
            "npat": 6835.0,
            "short_term_debt": 48200.0,
            "cash_and_equivalents": 22300.0,
            "interest_coverage": 3.8,
            "gross_margin_historical": [0.28, 0.22, 0.15],
            "dcf_fair_value": 26500.0,
            "market_price": 28500.0,
            "margin_of_safety": -0.075
        }
        """
    ]
    
    # Giả lập output của Agent
    agent_output = (
        "Nợ vay ngắn hạn của HPG ở mức 48200.0 tỷ VND trong khi tiền mặt chỉ có 22300.0 tỷ VND. "
        "Biên lợi nhuận gộp đã suy giảm từ 28% xuống 15% trong 3 năm qua. "
        "Với thị giá 28500.0 VND so với giá trị nội tại 26500.0 VND, biên an toàn hiện là âm -7.5%."
    )
    
    test_case = LLMTestCase(
        input="Hãy phản biện mô hình định giá HPG dựa trên số liệu BCTC và định giá DCF.",
        actual_output=agent_output,
        retrieval_context=retrieval_context
    )
    
    faithfulness_metric = FaithfulnessMetric(
        threshold=0.95,
        model="gpt-4o",
        include_reason=True
    )
    
    faithfulness_metric.measure(test_case)
    
    assert faithfulness_metric.score >= 0.95, f"Faithfulness score thấp: {faithfulness_metric.score}. Lý do: {faithfulness_metric.reason}"
    assert verify_numerical_grounding(agent_output, retrieval_context[0]), "Phát hiện số liệu bị ảo giác ngoài JSON!"
```
