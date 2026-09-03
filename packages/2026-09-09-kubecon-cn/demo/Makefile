.PHONY: help up baseline baseline-test reset-metrics open-dashboard load prefill-pressure pd-tune pd-validation gateway-error vllm-error gpu-error incident recovery request evidence status down down-cluster

SCENARIO ?=

help:
	@echo "make up              Create/update the kind demo environment"
	@echo "make baseline-test   Reset baseline and run automated acceptance checks"
	@echo "make reset-metrics   Clear Prometheus history and start a fresh baseline"
	@echo "make open-dashboard  Open the Grafana dashboard"
	@echo "Primary PD-disaggregated incident story (fixed 3P x 2D demo topology):"
	@echo "make baseline        Healthy service"
	@echo "make incident        Request pressure exposes KV-cache/Prefill failure"
	@echo "make evidence        Auto-detect active scenario; show colored health/alert evidence"
	@echo "make recovery        Remove the incident without changing P:D"
	@echo "make request         Send one real OpenAI-compatible request"
	@echo "make status          Print pods, scrape targets, scenario and key metrics"
	@echo ""
	@echo "Other fault fingerprints: make load | gateway-error | vllm-error | gpu-error"
	@echo "Override evidence scenario: make evidence SCENARIO=gpu_error"
	@echo "Optional tuning lab: make prefill-pressure | pd-tune | pd-validation"
	@echo "make down            Remove the namespace; make down-cluster removes kind"

up:
	./scripts/up.sh

baseline:
	./scripts/scenario.sh baseline

baseline-test:
	./scripts/baseline-test.sh

reset-metrics:
	./scripts/reset-metrics.sh

open-dashboard:
	./scripts/open-dashboard.sh

load:
	./scripts/scenario.sh load

prefill-pressure:
	./scripts/scenario.sh prefill_pressure

pd-tune:
	./scripts/scenario.sh pd_tuned

pd-validation:
	./scripts/pd-validation.sh

gateway-error:
	./scripts/scenario.sh gateway_error

vllm-error:
	./scripts/scenario.sh vllm_error

gpu-error:
	./scripts/scenario.sh gpu_error

incident:
	./scripts/scenario.sh incident

recovery:
	./scripts/scenario.sh recovery

request:
	./scripts/request.sh

evidence:
	./scripts/evidence.sh "$(SCENARIO)"

status:
	./scripts/status.sh

down:
	./scripts/down.sh

down-cluster:
	./scripts/down.sh --cluster
