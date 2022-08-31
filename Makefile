export DOCKER_BUILDKIT	:=	1

.PHONY: test lint-check lint-fix

test:
	docker build -f Dockerfile.tests -t sherpa-test .
	docker run sherpa-test

lint-check:
	black --check --diff sherpa
	autoflake --check -ri --ignore-init-module-imports --remove-all-unused-imports sherpa
	mypy -p sherpa

lint-fix:
	black sherpa
	autoflake -ri --ignore-init-module-imports --remove-all-unused-imports sherpa
	mypy -p sherpa
