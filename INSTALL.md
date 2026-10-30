# Installation

## Requirements

Linux, macOS or Windows (WSL), Python 3.10-3.13, git. No GPU or display:
geometry, renders and checks all run headless.

## Setup

```bash
git clone <repo> code-cad && cd code-cad
./install.sh
```

`install.sh` creates `.venv`, installs `requirements.txt` and the package in
editable mode, then builds an example as a self-test. On Debian/Ubuntu systems
without `python3-venv` it creates the venv without pip and bootstraps pip with
the system pip, so no `sudo apt install` is needed.

Manual equivalent:

```bash
python3 -m venv .venv            # or: python3 -m venv --without-pip .venv && python3 -m pip --python .venv/bin/python install pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install -e .
.venv/bin/python -m pytest -q    # 24 tests
```

Optional: `.venv/bin/python -m pip install bd_warehouse` for threads, gears,
bearings and ISO fastener solids.

## Claude Code

Run `claude` inside the repo. It picks up:

- `CLAUDE.md` - project rules;
- `.claude/skills/cad/` - the `/cad` skill (also triggers automatically on 3D-printing requests);
- `.claude/agents/cad-*.md` - the researcher, scout and two verifier agents.

If you add the `.claude/agents/` folder while Claude Code is running, restart
it once so the agents are registered.

### Use it from any directory

```bash
./install.sh --global
```

This links the skill and the agents into `~/.claude/` and `bin/cad` into
`~/.local/bin/` (make sure that is on your `PATH`).

## Other agents

`SKILL.md` at the repo root is a portable summary for agents that read a
single skill file (Antigravity, Codex, etc.). Those agents need a way to run
sub-agents for the independent verification steps; otherwise run the verifier
prompts in `.claude/agents/` in separate sessions.
