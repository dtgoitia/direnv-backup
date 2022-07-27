run:
	python bin.py

install-dev-tools:
	pre-commit install  # defaults to "pre-commit" stage

uninstall-dev-tools:
	pre-commit uninstall  # defaults to "pre-commit" stage

compile_production_dependencies:
	find ./requirements -type f -name "prod.txt" -delete
	pip-compile requirements/prod.in \
		--output-file requirements/prod.txt \
		--no-header \
		--no-emit-index-url \
		--verbose

compile_development_dependencies:
	find ./requirements -type f -name "dev.txt" -delete
	pip-compile requirements/prod.in requirements/dev.in \
		--output-file requirements/dev.txt \
		--no-header \
		--no-emit-index-url \
		--verbose

install_production_dependencies:
	pip install -r requirements/prod.txt

install_development_dependencies:
	pip install -r requirements/dev.txt

lint:
	flake8
	black --check --diff .
	isort --check --diff .
	python -m mypy --config-file setup.cfg --pretty .

format:
	isort .
	black .

test:
	pytest . -vv -s
