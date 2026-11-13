# ==============================================================================
# ValueInvest-Engine: Developer Automation & Task Runner
# ==============================================================================

.PHONY: help install lint format test eval run-api run-ui docker-up docker-down clean

help:
	@echo "========================================================================"
	@echo " ValueInvest-Engine: Production Automation Makefile"
	@echo "========================================================================"
	@echo "  make install     Install all dependencies including development tools"
	@echo "  make lint        Run Ruff linter and architectural boundary checks"
	@echo "  make format      Auto-format codebase using Ruff"
	@echo "  make test        Run deterministic engine unit tests with coverage"
	@echo "  make eval        Run DeepEval Faithfulness evaluation on Golden Dataset"
	@echo "  make run-api     Launch FastAPI REST Gateway on port 8000"
	@echo "  make run-ui      Launch Streamlit Dashboard on port 8501"
	@echo "  make docker-up   Build and start containers (App + Redis Cache)"
	@echo "  make docker-down Stop and remove docker containers"
	@echo "  make clean       Remove temporary Python cache and build artifacts"
	@echo "========================================================================"

install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e .[dev]

lint:
	@echo "--> Checking architectural boundaries..."
	python -c "import sys, re, glob; forbidden = [f for f in glob.glob('src/engine/**/*.py', recursive=True) + glob.glob('src/valuation/**/*.py', recursive=True) if re.search(r'import (langchain|langgraph|openai|instructor|litellm)', open(f).read())]; sys.exit('Violations in: ' + str(forbidden)) if forbidden else print('Boundary OK: Deterministic Engine is isolated.')"
	@echo "--> Running Ruff linter..."
	ruff check src/ tests/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

test:
	pytest tests/ -v --cov=src/engine --cov=src/valuation --cov-report=term-missing

eval:
	python -m pytest tests/test_llm_faithfulness.py -v -s -m evals

run-api:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

run-ui:
	streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('.pytest_cache')]; [p.unlink() for p in pathlib.Path('.').glob('dump.rdb')]"
