from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ["PT2VHF_WIN7_LEGACY"] = "1"


def _version_probe() -> bool:
    if "--write-version" not in sys.argv:
        return False
    try:
        idx = sys.argv.index("--write-version")
        target = Path(sys.argv[idx + 1]).expanduser()
    except Exception:
        return True
    from pt2vhf_aprs import __version__
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(__version__ + "\n", encoding="utf-8")
    return True


if _version_probe():
    raise SystemExit(0)

from windows_app import main


if __name__ == "__main__":
    raise SystemExit(main())
