venv:
	python -m venv .venv

install:
	source .venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt

run:
	echo "App will be added in next step"
