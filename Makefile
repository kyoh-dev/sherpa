export DOCKER_BUILDKIT	:=	1

.PHONY: test lint-check lint-fix

test:
	docker compose up -d --wait dbtest
	python -m pytest tests -vvv

lint-check:
	ls -lah
	black --check --diff sherpa
	autoflake --check -ri --ignore-init-module-imports --remove-all-unused-imports sherpa
	mypy -p sherpa

lint-fix:
	black sherpa
	autoflake -ri --ignore-init-module-imports --remove-all-unused-imports sherpa
	mypy -p sherpa
