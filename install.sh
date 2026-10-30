#!/usr/bin/env bash
# Set up code-cad: virtualenv + dependencies. Optional: --global also links the
# skill and agents into ~/.claude and `cad` into ~/.local/bin so /cad works in
# any project.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [ ! -x .venv/bin/python ]; then
  if ! python3 -m venv .venv 2>/dev/null; then
    # Debian/Ubuntu without python3-venv: create without pip, bootstrap with system pip
    rm -rf .venv
    python3 -m venv --without-pip .venv
    python3 -m pip --python .venv/bin/python install pip
  fi
fi
.venv/bin/python -m pip install -q --upgrade pip
.venv/bin/python -m pip install -q -r requirements.txt
.venv/bin/python -m pip install -q -e .
echo "venv ready: $ROOT/.venv"

if [ "${1:-}" = "--global" ]; then
  mkdir -p "$HOME/.claude/skills" "$HOME/.claude/agents" "$HOME/.local/bin"
  ln -sfn "$ROOT/.claude/skills/cad" "$HOME/.claude/skills/cad"
  for a in "$ROOT"/.claude/agents/cad-*.md; do ln -sfn "$a" "$HOME/.claude/agents/$(basename "$a")"; done
  ln -sfn "$ROOT/bin/cad" "$HOME/.local/bin/cad"
  echo "linked skill + agents into ~/.claude and cad into ~/.local/bin"
  echo "outside this repo, the skill calls 'cad' from PATH; projects go to $ROOT/projects"
fi

./bin/cad build examples/06_gridfinity_bin >/dev/null && echo "self-test OK (examples/06_gridfinity_bin built)"
