from __future__ import annotations

import os

# Windows 7 Legacy uses an isolated runtime/build, but it is still a desktop
# application. Never force --browser here. The embedded window uses the
# Windows renderer selected below; browser mode remains an explicit CLI option.
os.environ["PT2VHF_WIN7_LEGACY"] = "1"
os.environ.setdefault("PT2VHF_WEBVIEW_GUI", "edgechromium")

from windows_app import main


if __name__ == "__main__":
    raise SystemExit(main())
