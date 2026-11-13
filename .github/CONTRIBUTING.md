# Contributing to ValueInvest-Engine

Chào mừng bạn đến với dự án **ValueInvest-Engine**! Dự án tuân thủ nghiêm ngặt mô hình **Spec-Driven Development** và **Decoupled Architecture** nhằm loại bỏ hoàn toàn hiện tượng ảo giác số học (Zero Math Hallucination) trong phân tích tài chính định lượng.

Mọi đóng góp (Pull Request, Issue) đều phải tuân theo các quy chuẩn kỹ thuật dưới đây.

---

## 1. GitHub Flow & Branching Model

- **Bảo vệ nhánh chính (`main`)**: Cấm tuyệt đối push trực tiếp lên `main` (`Direct push is disabled`). Nhánh `main` luôn ở trạng thái sẵn sàng deploy Production.
- Mọi tính năng, sửa lỗi, cập nhật tài liệu phải được thực hiện trên các nhánh riêng biệt rẽ nhánh từ `main`:
  - `feat/<phase>-<feature-name>`: Thêm tính năng mới (ví dụ: `feat/p1-dupont-calc`, `feat/p2-challenger-agent`).
  - `fix/<issue-name>`: Vá lỗi kỹ thuật hoặc sửa công thức toán (ví dụ: `fix/zero-interest-coverage`).
  - `test/<eval-name>`: Thêm unit test hoặc golden benchmark cases (ví dụ: `test/nvl-golden-case`).
  - `docs/<doc-name>`: Cập nhật tài liệu kỹ thuật, specs hoặc README.

---

## 2. Conventional Commits Standard

Mọi commit message phải tuân thủ chuẩn [Conventional Commits v1.0.0](https://www.conventionalcommits.org/):

```
<type>(<scope>): <mô tả ngắn bằng tiếng Anh hoặc tiếng Việt>

[optional body: giải thích bối cảnh, lý do thay đổi]
[optional footer: Closes #issue-number]
```

### Các tiền tố hợp lệ:
- `feat(engine)`: Thêm logic tính toán mới trong `src/engine/`.
- `feat(valuation)`: Thêm mô hình định giá hoặc ma trận nhạy cảm trong `src/valuation/`.
- `feat(agents)`: Thêm hoặc tinh chỉnh tác tử trong `src/agents/`.
- `feat(llmops)`: Tích hợp tracing Langfuse, caching Redis, hoặc guardrails.
- `feat(ui)`: Cập nhật giao diện Streamlit hoặc Plotly chart.
- `fix(math)`: Sửa lỗi tính toán công thức kế toán/tài chính.
- `test(evals)`: Thêm test case DeepEval hoặc test unit Pytest.
- `ci`: Sửa cấu hình GitHub Actions workflow.
- `docs`: Cập nhật documentation, `.specs/`, hoặc README.

*Ví dụ:*
```bash
git commit -m "feat(valuation): implement vectorized 2D WACC vs g sensitivity matrix"
git commit -m "fix(engine): handle zero interest expense in interest coverage ratio"
```

---

## 3. Strict Quality Gates trước khi Merge PR

Một Pull Request chỉ được phép merge vào `main` khi vượt qua toàn bộ 4 điều kiện kiểm định tự động trong CI pipeline:

1. **Architectural Boundary Check**:
   - `src/engine/` và `src/valuation/` **tuyệt đối không import** bất kỳ package LLM nào (`langchain`, `langgraph`, `openai`, `instructor`, `litellm`, v.v.).
2. **Code Style & Type Checking**:
   - Code phải pass 100% kiểm tra linter của `ruff check src/ tests/`.
   - Type Hints đạt chuẩn 100%, pass `mypy`.
3. **Unit Test Coverage > 80%**:
   - Chạy Pytest đối chiếu với số liệu BCTC chuẩn:
     ```bash
     pytest tests/test_engine_math.py tests/test_red_flags.py --cov=src/engine --cov=src/valuation --cov-fail-under=80
     ```
4. **DeepEval Faithfulness Metric $\ge 0.95$**:
   - Chạy kiểm thử trên bộ dữ liệu `data/golden_eval/cases.json`.
   - Tác tử không được phép phát ngôn bất kỳ con số tài chính nào nằm ngoài dữ liệu JSON đầu vào.

---

## 4. Local Development Quickstart

```bash
# 1. Clone repository
git clone https://github.com/ThanhTan2k6/ValueInvest-Engine.git
cd ValueInvest-Engine

# 2. Khởi tạo virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Cài đặt dependencies
pip install -r requirements.txt

# 4. Sao chép biến môi trường
cp .env.example .env

# 5. Chạy unit tests cục bộ trước khi push
pytest tests/ -v
ruff check src/ tests/
```
