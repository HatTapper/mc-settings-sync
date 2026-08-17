"""Filesystem discovery for Prism instances and settings templates."""

import json
import os
from dataclasses import dataclass
from pathlib import Path

CONFIG_FILENAME = "mc-settings-sync.json"


def default_instances_root() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata).joinpath("PrismLauncher", "instances")
    return Path.home().joinpath(".local", "share", "PrismLauncher", "instances")


def default_templates_root() -> Path:
    return Path.home().joinpath("Documents", "MCTemplates")


def config_path() -> Path:
    appdata = os.environ.get("APPDATA")
    base = Path(appdata) if appdata else Path.home().joinpath(".config")
    return base.joinpath("mc-settings-sync", CONFIG_FILENAME)


@dataclass
class Settings:
    instances_root: Path
    templates_root: Path

    @classmethod
    def load(cls) -> "Settings":
        path = config_path()
        data = {}
        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                data = {}

        return cls(
            instances_root=Path(data.get("instances_root") or default_instances_root()),
            templates_root=Path(data.get("templates_root") or default_templates_root()),
        )

    def save(self) -> None:
        path = config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "instances_root": str(self.instances_root),
                    "templates_root": str(self.templates_root),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

# gets all mc instance paths present in a folder, using minecraft_dir() to verify
def list_instances(instances_root: Path) -> list[str]:
    if not instances_root.is_dir():
        return []
    
    names = []
    for entry in sorted(instances_root.iterdir(), key=lambda p: p.name.lower()):
        if entry.is_dir() and minecraft_dir(entry) is not None:
            names.append(entry.name)

    return names

# tries to fetch a potential mc instance given a path
def minecraft_dir(instance_dir: Path) -> Path | None:
    for candidate in ("minecraft", ".minecraft"):
        path = instance_dir.joinpath(candidate)
        if path.is_dir():
            return path
        
    return None


def list_templates(templates_root: Path) -> list[str]:
    if not templates_root.is_dir():
        return []

    return [
        entry.name
        for entry in sorted(templates_root.iterdir(), key=lambda p: p.name.lower())
        if entry.is_dir()
    ]


# makes the templates root plus a starter template, returning the starter folder
# safe to call when either already exists, nothing is overwritten
def create_starter_template(templates_root: Path, name: str = "base") -> Path:
    starter = templates_root.joinpath(name)
    starter.mkdir(parents=True, exist_ok=True)

    readme = templates_root.joinpath("README.txt")
    if not readme.exists():
        readme.write_text(STARTER_README, encoding="utf-8")

    return starter


# dropped next to the templates so the folder explains itself when opened
STARTER_README = """Each folder in here is one preset.

Put files in a preset exactly where they sit inside an instance's
'minecraft' folder, for example:

    base\\options.txt
    base\\servers.dat
    base\\config\\sodium-options.json

Applying a preset copies those files into the instance, overwriting any
file of the same name. Anything not in the preset is left alone.

Do not put 'saves' or 'mods' in a preset unless you mean it. Applying it
would overwrite worlds or mod files in the target instance.
"""
