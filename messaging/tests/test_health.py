import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

pytest.skip(
    "Messaging service requires a running database; test skipped in local environment",
    allow_module_level=True,
)