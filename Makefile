.PHONY: lint-check lint-fix

lint-check:
	black --check --diff sherpa
	autoflake --check -ri --ignore-init-module-imports --remove-all-unused-imports sherpa
	mypy -p sherpa

lint-fix:
	black sherpa
	autoflake -ri --ignore-init-module-imports --remove-all-unused-imports sherpa
	mypy -p sherpa
