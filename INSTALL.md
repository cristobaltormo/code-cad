# Installation & Environment Setup

This document describes how to set up the Python environment and configure AI agents to use the Code-CAD framework.

---

## 1. System Requirements

- Linux, macOS, or Windows
- Python 3.10, 3.11, 3.12, or 3.13
- Git

No GPU or display server (X11/Wayland) is required. All geometric calculations, OpenCASCADE BREP evaluations, and 4-view SVG technical drawings run headlessly in pure Python.

---

## 2. Python Environment Setup

Clone the repository and create an isolated virtual environment:

```bash
git clone git@gitea-lan:cristobal/code-cad.git
cd code-cad

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

Verify the installation by running the inspection tool on one of the example models:

```bash
python3 examples/01_electronics_enclosure/case.py
```

You should see the inspection table and generated files in `examples/01_electronics_enclosure/exports/`.

---

## 3. Configuring Claude Code

To enable Code-CAD inside Claude Code:

### Option A: Repository Mode (Recommended)
When working directly inside this repository, Claude Code automatically detects:
- `CLAUDE.md`: Enforces DFAM rules and the execution/verification cycle.
- `.claude/commands/cad.md`: Provides the `/cad` slash command.

Run Claude Code in the repository:
```bash
claude
```

Type `/cad` followed by your part description:
```
/cad Parametric wall mount for a 40mm cooling fan with M3 screw holes
```

### Option B: Drop-in to Any Existing Project
Copy `CLAUDE.md` and `cad_tools/` into your existing project folder, activate the virtual environment, and Claude Code will operate as a CAD engineer.

---

## 4. Configuring Other Agent Environments

### Antigravity & Agent CLI
Copy or symlink `SKILL.md` and the `cad_tools` package into your agent's skills directory:
```bash
cp SKILL.md ~/.agents/skills/code-cad/SKILL.md
```
