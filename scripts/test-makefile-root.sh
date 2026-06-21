#!/usr/bin/env sh
set -eu

PATH=/usr/bin:/bin
export PATH
MAKE_BIN=${MAKE_BIN:-/usr/bin/make}

if [ ! -x "$MAKE_BIN" ]; then
    echo "MAKE_BIN must name an executable make: $MAKE_BIN" >&2
    exit 1
fi

ROOT_DIR=$(CDPATH=; cd -- "$(dirname -- "$0")/.." && /bin/pwd -P)
TEMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/valleybot-make-authority-XXXXXX")
trap 'rm -rf "$TEMP_ROOT"' EXIT HUP INT TERM
unset MAKEFILES MAKEFILE_LIST MAKEFLAGS MFLAGS MAKEOVERRIDES ROOT SHELL

CONTROL_DIR="$TEMP_ROOT/control"
CHECKOUT="$TEMP_ROOT/valleybot app's [gate] \"quoted\" \`touch VALLEYBOT_ROOT_MARKER\`"
ATTACKER_ROOT="$TEMP_ROOT/attacker"
LOG="$TEMP_ROOT/commands.log"
SHELL_LOG="$TEMP_ROOT/shell.log"

mkdir -p "$CONTROL_DIR" "$CHECKOUT/scripts" "$ATTACKER_ROOT"
CONTROL_DIR=$(CDPATH=; cd -- "$CONTROL_DIR" && /bin/pwd -P)
CHECKOUT=$(CDPATH=; cd -- "$CHECKOUT" && /bin/pwd -P)
MAKEFILE="$CHECKOUT/Makefile"
cp "$ROOT_DIR/Makefile" "$MAKEFILE"

FAKE_PYTHON="$TEMP_ROOT/trusted python's \"quoted\" \`touch VALLEYBOT_PYTHON_MARKER\` \$literal"
cat >"$FAKE_PYTHON" <<'EOF'
#!/bin/sh
printf '%s|%s|%s\n' "$PWD" "$0" "$*" >> "$VALLEYBOT_COMMAND_LOG"
EOF
chmod +x "$FAKE_PYTHON"

for script in test-makefile-root.sh check_valleybot_contracts.py test_web_chat_length_contract.py prepare_nltk_data.sh; do
    cp "$FAKE_PYTHON" "$CHECKOUT/scripts/$script"
done
for file in app.py bot.py bot_tests.py config.py nltk_guard.py settings.py slack_auth.py slack_replay.py slack.py; do
    : >"$CHECKOUT/$file"
done

FAKE_SHELL="$TEMP_ROOT/fake-shell"
cat >"$FAKE_SHELL" <<EOF
#!/bin/sh
printf invoked >> '$SHELL_LOG'
exec /bin/sh "\$@"
EOF
chmod +x "$FAKE_SHELL"

make_run() {
    "$MAKE_BIN" --no-print-directory "$@"
}

run_case() {
    target=$1
    mode=$2
    rm -f "$LOG" "$SHELL_LOG"
    : >"$CHECKOUT/probe.pyc"
    : >"$ATTACKER_ROOT/keep.pyc"
    set +e
    case "$mode" in
        default)
            (cd "$CONTROL_DIR" && VALLEYBOT_COMMAND_LOG="$LOG" make_run -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "$target") >/dev/null 2>&1
            ;;
        command-root)
            (cd "$CONTROL_DIR" && VALLEYBOT_COMMAND_LOG="$LOG" make_run -f "$MAKEFILE" ROOT="$ATTACKER_ROOT" "PYTHON=$FAKE_PYTHON" "$target") >/dev/null 2>&1
            ;;
        environment-root)
            (cd "$CONTROL_DIR" && ROOT="$ATTACKER_ROOT" VALLEYBOT_COMMAND_LOG="$LOG" make_run -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "$target") >/dev/null 2>&1
            ;;
        command-shell)
            (cd "$CONTROL_DIR" && VALLEYBOT_COMMAND_LOG="$LOG" make_run -f "$MAKEFILE" SHELL="$FAKE_SHELL" "PYTHON=$FAKE_PYTHON" "$target") >/dev/null 2>&1
            ;;
        environment-shell)
            (cd "$CONTROL_DIR" && SHELL="$FAKE_SHELL" VALLEYBOT_COMMAND_LOG="$LOG" make_run -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "$target") >/dev/null 2>&1
            ;;
    esac
    status=$?
    set -e
    [ "$status" -eq 0 ]
    [ ! -e "$SHELL_LOG" ]
    [ -e "$ATTACKER_ROOT/keep.pyc" ]
    case "$target" in
        clean) [ ! -e "$CHECKOUT/probe.pyc" ] ;;
        *) grep -Fq "$CHECKOUT" "$LOG" ;;
    esac
}

executed=0
for target in build check clean lint prepare-corpora root-test test verify; do
    for mode in default command-root environment-root command-shell environment-shell; do
        run_case "$target" "$mode"
        executed=$((executed + 1))
    done
done
[ "$executed" -eq 40 ]

rm -f "$LOG"
(cd "$CONTROL_DIR" && VALLEYBOT_COMMAND_LOG="$LOG" make_run -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" check) >/dev/null 2>&1
grep -Fq "$FAKE_PYTHON" "$LOG"
[ ! -e "$CONTROL_DIR/VALLEYBOT_ROOT_MARKER" ]
[ ! -e "$CONTROL_DIR/VALLEYBOT_PYTHON_MARKER" ]

MARK="$TEMP_ROOT/python-syntax"
BAD="\$(shell /usr/bin/touch '$MARK')"
if (cd "$CONTROL_DIR" && make_run -f "$MAKEFILE" "PYTHON=$BAD" lint) >"$TEMP_ROOT/python.out" 2>&1; then
    exit 1
fi
[ ! -e "$MARK" ]

ENV_MARK="$TEMP_ROOT/python-environment-syntax"
ENV_BAD="\$(shell /usr/bin/touch '$ENV_MARK')"
if (cd "$CONTROL_DIR" && PYTHON="$ENV_BAD" make_run --environment-overrides -f "$MAKEFILE" lint) >"$TEMP_ROOT/python-environment.out" 2>&1; then
    exit 1
fi
[ ! -e "$ENV_MARK" ]

if (cd "$CONTROL_DIR" && make_run -f "$MAKEFILE" MAKEFILE_LIST=/tmp/untrusted check) >"$TEMP_ROOT/list" 2>&1; then
    exit 1
fi
grep -Fq 'MAKEFILE_LIST must not be overridden' "$TEMP_ROOT/list"

if (cd "$CONTROL_DIR" && MAKEFILE_LIST=/tmp/untrusted make_run --environment-overrides -f "$MAKEFILE" check) >"$TEMP_ROOT/list-environment" 2>&1; then
    exit 1
fi
grep -Fq 'MAKEFILE_LIST must not be overridden' "$TEMP_ROOT/list-environment"

PRE="$TEMP_ROOT/pre.mk"
PRE_MARKER="$TEMP_ROOT/pre-ran"
printf '%s\n' "\$(shell /usr/bin/touch '$PRE_MARKER')" >"$PRE"
if (cd "$CONTROL_DIR" && MAKEFILES="$PRE" make_run -f "$MAKEFILE" check) >"$TEMP_ROOT/pre" 2>&1; then
    exit 1
fi
grep -Fq 'MAKEFILES must be empty' "$TEMP_ROOT/pre"
[ -e "$PRE_MARKER" ]

EARLY="$TEMP_ROOT/early.mk"
EARLY_MARKER="$TEMP_ROOT/early-ran"
printf '%s\n' "\$(shell /usr/bin/touch '$EARLY_MARKER')" >"$EARLY"
if (cd "$CONTROL_DIR" && make_run -f "$EARLY" -f "$MAKEFILE" check) >"$TEMP_ROOT/early" 2>&1; then
    exit 1
fi
[ -s "$TEMP_ROOT/early" ]
[ -e "$EARLY_MARKER" ]

GLOBAL_SHELL="$TEMP_ROOT/global-override-shell"
GLOBAL_SHELL_LOG="$TEMP_ROOT/global-override-shell.log"
GLOBAL_OVERRIDE="$TEMP_ROOT/global-override.mk"
cat >"$GLOBAL_SHELL" <<'EOF'
#!/bin/sh
printf '%s\n' "$*" >> "$VALLEYBOT_GLOBAL_OVERRIDE_LOG"
printf ok
exit 0
EOF
chmod +x "$GLOBAL_SHELL"
printf 'override SHELL := %s\noverride .SHELLFLAGS := -c\n' "$GLOBAL_SHELL" >"$GLOBAL_OVERRIDE"
if ! (cd "$CONTROL_DIR" && VALLEYBOT_GLOBAL_OVERRIDE_LOG="$GLOBAL_SHELL_LOG" make_run -f "$MAKEFILE" -f "$GLOBAL_OVERRIDE" PYTHON=/bin/false lint) >"$TEMP_ROOT/global-override" 2>&1; then
    exit 1
fi
[ -s "$GLOBAL_SHELL_LOG" ]
grep -Fq 'py_compile' "$GLOBAL_SHELL_LOG"

if (cd "$CONTROL_DIR" && make_run -f "$MAKEFILE" MAKEFLAGS=-n check) >"$TEMP_ROOT/flags" 2>&1; then
    exit 1
fi
grep -Fq 'MAKEFLAGS must not be overridden' "$TEMP_ROOT/flags"

for flag in -n --just-print --dry-run --recon -t --touch -q --question -i --ignore-errors; do
    if (cd "$CONTROL_DIR" && make_run "$flag" -f "$MAKEFILE" check) >"$TEMP_ROOT/flag" 2>&1; then
        exit 1
    fi
    grep -Fq 'non-executing or error-ignoring MAKEFLAGS are not supported' "$TEMP_ROOT/flag"
done

printf '%s\n' 'Make authority tests passed: 40 target/authority cases, literal hostile Python path, 2 raw Make-syntax rejections, 2 MAKEFILE_LIST rejections, 2 startup-boundary cases, cleanup containment, caller MAKEFLAGS rejection, global override shell boundary control showing caller global override SHELL can make a failing Python tool look successful, and 10 unsafe mode rejections'
