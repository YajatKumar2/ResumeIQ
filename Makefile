PYTHON := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: help setup test backend frontend build sample calibrate llm-status verify

help:
	@echo "ResumeIQ commands:"
	@echo "  make setup      Install backend and frontend dependencies"
	@echo "  make test       Run backend tests with the project virtual environment"
	@echo "  make backend    Start FastAPI backend on http://127.0.0.1:8000"
	@echo "  make frontend   Start React frontend on http://127.0.0.1:5173"
	@echo "  make build      Build the frontend"
	@echo "  make sample     Run sample resume analysis"
	@echo "  make calibrate  Run scoring calibration examples"
	@echo "  make llm-status Show optional LLM configuration status"
	@echo "  make verify     Run tests, calibration, and frontend build"

setup:
	python3 -m venv .venv
	$(PIP) install -r requirements.txt
	cd frontend && npm install

test:
	$(PYTHON) -m pytest

backend:
	$(PYTHON) -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

frontend:
	cd frontend && npm run dev -- --host 127.0.0.1

build:
	cd frontend && npm run build

sample:
	$(PYTHON) backend/scripts/analyze_sample.py

calibrate:
	$(PYTHON) backend/scripts/evaluate_samples.py

llm-status:
	$(PYTHON) backend/scripts/check_llm_config.py

verify: test calibrate build
