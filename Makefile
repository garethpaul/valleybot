PYTHON ?= python3
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

PYTHON_FILES := \
	app.py \
	bot.py \
	bot_tests.py \
	config.py \
	settings.py \
	slack.py \
	scripts/check_valleybot_contracts.py

.PHONY: clean lint prepare-corpora test build verify check

check: clean verify
	$(MAKE) -f "$(ROOT)/Makefile" clean

clean:
	find "$(ROOT)" -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	find "$(ROOT)" -type d -name '__pycache__' -prune -exec rm -rf {} +

lint:
	cd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m py_compile $(PYTHON_FILES)

prepare-corpora:
	PYTHON=$(PYTHON) "$(ROOT)/scripts/prepare_nltk_data.sh"

test: prepare-corpora
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/check_valleybot_contracts.py"
	cd "$(ROOT)" && env SLACK_TOKEN=test-slack-token MESSENGER_TOKEN=test-page-token MESSENGER_VERIFY_TOKEN=test-verify-token $(PYTHON) -m unittest bot_tests

build: lint

verify: lint test build
