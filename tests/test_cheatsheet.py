"""Every python block in the build123d cheat sheet must run."""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SHEET = ROOT / ".claude/skills/cad/references/build123d-cheatsheet.md"
BLOCKS = re.findall(r"```python\n(.*?)```", SHEET.read_text(), re.S)


@pytest.mark.parametrize("i", range(len(BLOCKS)))
def test_block(i):
    sys.path.insert(0, str(ROOT))
    exec(compile(BLOCKS[i], f"cheatsheet_block_{i}", "exec"), {})
