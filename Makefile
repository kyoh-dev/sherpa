lint:
	black sherpa
	autoflake -ri --ignore-init-module-imports --remove-all-unused-imports sherpa
	mypy -p sherpa
