
test = poetry run pytest --capture=fd --verbosity=0

dev:
	fastapi dev app/main.py

prod:
	fastapi run app/main.py

lint:
	poetry run ruff format --check app tests
	poetry run ruff check app tests
	poetry run toml-sort pyproject.toml --check

fmt:
	poetry run ruff format app tests
	poetry run ruff check --select I --fix  # sort imports
	poetry run toml-sort pyproject.toml

test:
	${test}

testparallel:
	${test} -n auto

testwithcoverage:
	$(test) \
		--cov=app \
		--cov-report=term-missing:skip-covered \
		--cov-fail-under=90
