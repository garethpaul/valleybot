.DEFAULT_GOAL := check
.PHONY: __repository-make-authority build check clean lint prepare-corpora root-test test verify
.SECONDEXPANSION:

PYTHON ?= python3
override PYTHON := $(value PYTHON)
export PYTHON
override REPOSITORY_MAKE_DOLLAR := $$
override REPOSITORY_MAKE_OPEN := (
ifneq ($(findstring $(REPOSITORY_MAKE_DOLLAR)$(REPOSITORY_MAKE_OPEN),$(value PYTHON)),)
$(error PYTHON must be a literal executable path, not Make syntax)
endif
override SHELL := /bin/sh
override .SHELLFLAGS := -c

ifneq ($(filter command line,$(origin MAKEFLAGS)),)
$(error MAKEFLAGS must not be overridden for repository verification)
endif
override REPOSITORY_MAKE_FIRST_FLAGS := $(firstword $(MAKEFLAGS))
ifneq ($(filter -%,$(REPOSITORY_MAKE_FIRST_FLAGS)),)
override REPOSITORY_MAKE_FIRST_FLAGS :=
endif
override REPOSITORY_MAKE_SHORT_FLAGS := $(REPOSITORY_MAKE_FIRST_FLAGS) $(filter-out --%,$(filter -%,$(MAKEFLAGS)))
ifneq ($(findstring n,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring t,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring q,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring i,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(filter --just-print --dry-run --recon --touch --question --ignore-errors,$(MAKEFLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(strip $(MAKEFILES)),)
$(error MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone)
endif
override MAKEFILES :=
ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell path='$(subst ','"'"',$(value MAKEFILE_LIST))'; path=$$(printf '%s' "$$path" | /usr/bin/sed 's/^ //'); [ -f "$$path" ] || exit 1; directory=$$(/usr/bin/dirname -- "$$path"); CDPATH= cd -- "$$directory" && /bin/pwd -P)
export ROOT
ifeq ($(strip $(ROOT)),)
$(error repository Makefile path could not be resolved)
endif

PYTHON_FILES := \
	app.py \
	bot.py \
	bot_tests.py \
	config.py \
	nltk_guard.py \
	settings.py \
	slack_auth.py \
	slack_replay.py \
	slack.py \
	scripts/check_valleybot_contracts.py \
	scripts/test_web_chat_length_contract.py

build check clean lint prepare-corpora root-test test verify: $$(if $$(filter file,$$(origin MAKEFILE_LIST)),,$$(error MAKEFILE_LIST must not be overridden))
build check clean lint prepare-corpora root-test test verify: $$(if $$(shell path=$$$$(/usr/bin/printf '%s' '$$(subst ','"'"',$$(MAKEFILE_LIST))' | /usr/bin/sed 's/^ //') && [ -f "$$$$path" ] && /usr/bin/printf '%s' ok),,$$(error repository Makefile must be loaded alone))
build check clean lint prepare-corpora root-test test verify: __repository-make-authority

__repository-make-authority::
	@:

clean:
	/usr/bin/find "$$ROOT" -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	/usr/bin/find "$$ROOT" -type d -name '__pycache__' -prune -exec /bin/rm -rf {} +

lint:
	cd "$$ROOT" && PYTHONDONTWRITEBYTECODE=1 "$$PYTHON" -m py_compile $(PYTHON_FILES)

prepare-corpora:
	PYTHON="$$PYTHON" "$$ROOT/scripts/prepare_nltk_data.sh"

test: prepare-corpora
	PYTHONDONTWRITEBYTECODE=1 "$$PYTHON" "$$ROOT/scripts/check_valleybot_contracts.py"
	PYTHONDONTWRITEBYTECODE=1 "$$PYTHON" "$$ROOT/scripts/test_web_chat_length_contract.py"
	cd "$$ROOT" && /usr/bin/env SLACK_SIGNING_SECRET=test-slack-signing-secret MESSENGER_TOKEN=test-page-token MESSENGER_VERIFY_TOKEN=test-verify-token "$$PYTHON" -m unittest bot_tests

build: lint

root-test:
	/bin/sh "$$ROOT/scripts/test-makefile-root.sh"

verify: root-test lint test build

check: clean verify
	/usr/bin/find "$$ROOT" -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	/usr/bin/find "$$ROOT" -type d -name '__pycache__' -prune -exec /bin/rm -rf {} +
