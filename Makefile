environment: venv/bin/activate
venv/bin/activate: requirements.txt
	virtualenv --prompt="(flask_storm)" venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install -e .
	touch "$@"

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -type d -name '__pycache__' -exec rm -rf {} +

clean-doc:
	rm -rf doc/_build

clean: clean-pyc clean-doc
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

test:
	venv/bin/python -m pytest

build: clean test
	python setup.py sdist bdist_wheel

release: build
	python setup.py upload

.PHONY: build clean clean-doc clean-pyc environment release test
