#!/usr/bin/env python
"""Quick test runner script"""

import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
    cwd="/workspaces/skills-getting-started-with-github-copilot"
)

sys.exit(result.returncode)
