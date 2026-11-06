import os
import sys


def _get_project_root():
    if getattr(sys, "frozen", False):
        # Running as a PyInstaller .exe: use the folder the .exe is in
        return os.path.dirname(os.path.abspath(sys.executable))
    # Running as a normal .py file: use this project's folder
    return os.path.dirname(os.path.abspath(__file__))


def _get_bundle_root():
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


PROJECT_ROOT = _get_project_root()
BUNDLE_ROOT = _get_bundle_root()

# make sure the folders we write into always exist
os.makedirs(os.path.join(PROJECT_ROOT, "data"), exist_ok=True)
os.makedirs(os.path.join(PROJECT_ROOT, "db"), exist_ok=True)
