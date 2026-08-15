# mc-settings-sync

Copies pre-configured Minecraft settings — `options.txt`, `servers.dat`,
`config/sodium-options.json`, `config/iris.properties`, and anything else you
drop in a template folder — into a Prism Launcher instance, so a fresh (or
modded) instance doesn't have to be reconfigured by hand.

Only files that exist in the template are written. `saves/`, `mods/`,
`resourcepacks/`, and any other mod configs in the instance are left untouched.

## Setup

Templates live in subfolders of `Documents\MCTemplates`, one folder per
template, mirroring the layout of an instance's `minecraft` folder:

```
Documents\MCTemplates\
  base\
    options.txt
    servers.dat
    config\sodium-options.json
  fabric-sodium\
    options.txt
    config\iris.properties
```

The easiest way to make one: configure an instance the way you like it, then copy
the files you care about out of
`%APPDATA%\PrismLauncher\instances\<Instance>\minecraft` into a new template
folder.

## Usage

Download `mc-settings-sync.exe` from
[Releases](https://github.com/HatTapper/mc-settings-sync/releases) and run it.
Pick an instance and a template from the dropdowns, then click **Apply
settings**. Both folder locations can be changed from the **Folders** section;
the choice is remembered in `%APPDATA%\mc-settings-sync\mc-settings-sync.json`.

The same executable also works from a terminal, matching the old `.bat` script:

```bash
mc-settings-sync.exe "Fabric 1.21" fabric-sodium
```

Pass `--dry-run` to list what would be copied without writing anything.

## Development

```bash
python -m pip install -e ".[dev]"
```

```bash
python -m pytest
```

```bash
python -m mc_settings_sync
```

Every push runs the tests and builds the `.exe` on Windows; pushing a `v*` tag
also attaches the executable to a GitHub Release.

## License

MIT — see [LICENSE](LICENSE).
