import shutil
import sys
import subprocess
import zipapp
import tempfile
from pathlib import Path

MAIN = """\
#!/usr/bin/env python

import os
import runpy
import sys

lib = os.path.join(os.path.dirname(__file__), "lib")
sys.path.insert(0, lib)

runpy.run_module("pip", run_name="__main__")
"""

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    (tmp / "__main__.py").write_text(MAIN, encoding="utf-8")
    lib = tmp / "lib"
    lib.mkdir()
    subprocess.run([
        sys.executable,
        "-m",
        "pip",
        "install",
        "--target", str(lib),
        "pip"
    ])

    distinfo = list(lib.glob("pip*.dist-info"))
    if len(distinfo) != 1:
        print("Pip install failed, no dist-info directory")
        raise SystemExit

    distinfo = distinfo[0]
    distinfo_name = distinfo.name
    if not distinfo_name.startswith("pip-"):
        print(f"Pip install failed, invalid dist-info directory {distinfo}")
        raise SystemExit

    pipversion = distinfo_name[4:-10]

    shutil.rmtree(lib / "bin")
    shutil.rmtree(distinfo)


    zipapp.create_archive(
        tmp,
        target=f"pip-{pipversion}.pyz",
        interpreter="/usr/bin/env python"
    )
