# pyinstaller entry point
# the package's own __main__ cannot be frozen directly, running it as a script
# leaves it without a parent package and its relative imports fail
import sys

from mc_settings_sync.__main__ import main

if __name__ == "__main__":
    sys.exit(main())
