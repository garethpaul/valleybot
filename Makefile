PYTHON ?= python
PYTHON2 ?= python2

PYTHON_FILES := \
	app.py \
	bot.py \
	bot_tests.py \
	config.py \
	settings.py \
	slack.py \
	scripts/check_valleybot_contracts.py

.PHONY: clean lint test build verify check

check: clean verify
	$(MAKE) clean

clean:
	find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +

lint:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m py_compile $(PYTHON_FILES)

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) scripts/check_valleybot_contracts.py
	@if command -v $(PYTHON2) >/dev/null 2>&1 && $(PYTHON2) -c "import bottle, nltk, requests, textblob, webtest" >/dev/null 2>&1; then \
		env SLACK_TOKEN=test-slack-token MESSENGER_TOKEN=test-page-token MESSENGER_VERIFY_TOKEN=test-verify-token $(PYTHON2) -m unittest bot_tests; \
	else \
		echo "Skipping legacy Python 2 bot_tests: dependencies are not installed."; \
	fi

build: lint

verify: lint test build
