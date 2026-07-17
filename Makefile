.DEFAULT_GOAL := check
.PHONY: __repository-make-authority build check clean lint prepare-corpora root-test test verify
.SECONDEXPANSION:

ifeq ($(origin PYTHON),undefined)
override PYTHON := /usr/bin/python3
else
override PYTHON := $(value PYTHON)
endif
export PYTHON
override REPOSITORY_MAKE_DOLLAR := $$
override REPOSITORY_MAKE_OPEN := (
ifneq ($(findstring $(REPOSITORY_MAKE_DOLLAR)$(REPOSITORY_MAKE_OPEN),$(value PYTHON)),)
$(error PYTHON must be a literal executable path, not Make syntax)
endif
ifneq ($(findstring $(REPOSITORY_MAKE_DOLLAR){,$(value PYTHON)),)
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
override REPOSITORY_MAKEFILE_LIST := $(value MAKEFILE_LIST)
override ROOT := $(shell path='$(subst ','"'"',$(value MAKEFILE_LIST))'; path=$$(printf '%s' "$$path" | /usr/bin/sed 's/^ //'); [ -f "$$path" ] || exit 1; directory=$$(/usr/bin/dirname -- "$$path"); CDPATH='' cd -- "$$directory" && /bin/pwd -P)
export ROOT
ifeq ($(strip $(ROOT)),)
$(error repository Makefile path could not be resolved)
endif
override REPOSITORY_SHELL_LITERAL = $(subst $$,$$$$,$(subst ','"'"',$1))
override REPOSITORY_PARSE_SHELL_LITERAL = $(subst ','"'"',$1)
override REPOSITORY_ROOT_LITERAL := $(call REPOSITORY_SHELL_LITERAL,$(ROOT))
override REPOSITORY_PYTHON_LITERAL := $(call REPOSITORY_SHELL_LITERAL,$(PYTHON))
override REPOSITORY_PYTHON_IS_VALID := $(shell candidate='$(call REPOSITORY_PARSE_SHELL_LITERAL,$(PYTHON))'; /bin/expr "$$candidate" : '^/' >/dev/null && [ -x "$$candidate" ] && /usr/bin/printf '%s' yes)
ifneq ($(REPOSITORY_PYTHON_IS_VALID),yes)
$(error PYTHON must be an absolute executable path)
endif

PYTHON_FILES := \
	app.py \
	bot.py \
	bot_tests.py \
	channel_limits.py \
	config.py \
	nltk_guard.py \
	settings.py \
	slack_auth.py \
	slack_replay.py \
	slack.py \
	scripts/check_nltk_data.py \
	scripts/check_valleybot_contracts.py \
	scripts/test_slack_replay_mutations.py \
	scripts/test_web_chat_length_contract.py

build check clean lint prepare-corpora root-test test verify:: $$(if $$(filter file,$$(origin MAKEFILE_LIST)),,$$(error MAKEFILE_LIST must not be overridden))
build check clean lint prepare-corpora root-test test verify:: $$(if $$(filter-out $$(REPOSITORY_MAKEFILE_LIST),$$(value MAKEFILE_LIST)),$$(error repository Makefile must be loaded alone))
build check clean lint prepare-corpora root-test test verify:: $$(if $$(filter-out $$(value MAKEFILE_LIST),$$(REPOSITORY_MAKEFILE_LIST)),$$(error repository Makefile must be loaded alone))
build check clean lint prepare-corpora root-test test verify:: __repository-make-authority

__repository-make-authority::
	@:

define REPOSITORY_PUBLIC_RECIPES
clean::
	/usr/bin/find '$(REPOSITORY_ROOT_LITERAL)' -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	/usr/bin/find '$(REPOSITORY_ROOT_LITERAL)' -type d -name '__pycache__' -prune -exec /bin/rm -rf {} +

lint::
	cd '$(REPOSITORY_ROOT_LITERAL)' && PYTHONDONTWRITEBYTECODE=1 '$(REPOSITORY_PYTHON_LITERAL)' -I -B -m py_compile $(PYTHON_FILES)

prepare-corpora::
	REPOSITORY_PYTHON='$(REPOSITORY_PYTHON_LITERAL)' '$(REPOSITORY_ROOT_LITERAL)/scripts/prepare_nltk_data.sh'

test:: prepare-corpora
	REPOSITORY_PYTHON='$(REPOSITORY_PYTHON_LITERAL)' '$(REPOSITORY_ROOT_LITERAL)/scripts/run-python.sh' '$(REPOSITORY_ROOT_LITERAL)/scripts/check_valleybot_contracts.py'
	REPOSITORY_PYTHON='$(REPOSITORY_PYTHON_LITERAL)' '$(REPOSITORY_ROOT_LITERAL)/scripts/run-python.sh' '$(REPOSITORY_ROOT_LITERAL)/scripts/test_slack_replay_mutations.py'
	REPOSITORY_PYTHON='$(REPOSITORY_PYTHON_LITERAL)' '$(REPOSITORY_ROOT_LITERAL)/scripts/run-python.sh' '$(REPOSITORY_ROOT_LITERAL)/scripts/test_web_chat_length_contract.py'
	cd '$(REPOSITORY_ROOT_LITERAL)' && /usr/bin/env SLACK_SIGNING_SECRET=test-slack-signing-secret MESSENGER_TOKEN=test-page-token MESSENGER_VERIFY_TOKEN=test-verify-token REPOSITORY_PYTHON='$(REPOSITORY_PYTHON_LITERAL)' '$(REPOSITORY_ROOT_LITERAL)/scripts/run-python.sh' '$(REPOSITORY_ROOT_LITERAL)/bot_tests.py'

build:: lint

root-test::
	/bin/sh '$(REPOSITORY_ROOT_LITERAL)/scripts/test-makefile-root.sh'

verify:: root-test lint test build

check:: clean root-test verify
	/usr/bin/find '$(REPOSITORY_ROOT_LITERAL)' -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	/usr/bin/find '$(REPOSITORY_ROOT_LITERAL)' -type d -name '__pycache__' -prune -exec /bin/rm -rf {} +
endef
$(eval $(REPOSITORY_PUBLIC_RECIPES))
