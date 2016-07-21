environment: venv/bin/activate
venv/bin/activate: requirements.txt
	virtualenv --prompt="(flask_storm)" venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install -e .
	touch "$@"

.PHONY: environment
