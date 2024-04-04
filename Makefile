export DOCKER_BUILDKIT	:=	1

.PHONY: test lint-check lint-fix format

test:
	docker compose up -d --wait dbtest
	python -m pytest tests -vvv

lint-check:
	ruff check sherpa
	mypy -p sherpa

lint-fix:
	ruff check --fix sherpa
	mypy -p sherpa

format:
	ruff format sherpa tests
