"""Entry point: `python -m mc_settings_sync` opens the GUI.

With arguments it behaves like the original .bat script:
    python -m mc_settings_sync <InstanceName> [TemplateName]
"""

import argparse
import sys

from .paths import Settings
from .sync import SyncError, apply_template


def main(argv: list[str] | None = None) -> int:
    # ensure the args get through somehow
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        from .gui import main as gui_main

        return gui_main()

    parser = argparse.ArgumentParser(prog="MCSettingsSync")
    parser.add_argument("instance")
    parser.add_argument("template", nargs="?", default="base")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    settings = Settings.load()
    try:
        result = apply_template(
            settings.instances_root,
            args.instance,
            settings.templates_root,
            args.template,
            dry_run=args.dry_run,
        )
    except (SyncError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    verb = "Would copy" if args.dry_run else "Copied"
    print(f"{verb} {result.count} file(s) into {result.destination}")
    for name in result.copied:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
