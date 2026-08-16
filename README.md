# mc-settings-sync

Copies pre-configured Minecraft settings — `options.txt`, `servers.dat`,
`config/sodium-options.json`, `config/iris.properties`, and anything else you
drop in a template folder — into a launcher instance, so a fresh (or
modded) instance doesn't have to be reconfigured by hand.

Only files that exist in the template are written into the target instance.
In order to avoid unintended overwrites, it is suggested that you refrain from
including directories such as `saves/`, `mods/`, `resourcepacks/`, and any other
locations in the instance you wish to leave untouched.

Upon running the .exe, Windows will show an "unknown publisher" screen due to the application
not possessing a signed executable. To get past it, select "More Info" -> "Run anyway"

## Compatibility

| Launcher | Status |
| --- | --- |
| Prism Launcher | Confirmed working |
| MultiMC | Likely - same layout, untested |
| CurseForge | Not yet supported |
| Other | Try it, and open a [launcher support issue](../../issues/new?template=launcher-support-request.md) if instances don't appear |

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

If one cannot be found, the application offers the option to build the template root folder
for you automatically with the "Create templates folder" button. This is the recommended option.
You can choose to make one manually as well.

For bringing over your settings: configure an instance the way you like it, then copy
the files you care about out of
`%APPDATA%\PrismLauncher\instances\<Instance>\minecraft` into a new template
folder under your template root folder.

### Minecraft and mod versions

A template works best on instances close to the version it was built from.
`options.txt` ports well, since Minecraft ignores settings it does not
recognize and fills in defaults for any that are missing, and `servers.dat`
is version agnostic.

Mod configs are the ones to watch. Files like `sodium-options.json` and
`iris.properties` change format between mod releases, and an older config may
be reset to defaults or fail to load on a newer version of the mod. A config
for a mod the instance does not have is harmless, it simply sits unread.

Naming templates after what they were built for, such as `fabric-1.21-sodium`
rather than `fabric-sodium`, keeps this straight once you have a few.

## Usage

Download `mc-settings-sync.exe` from
[Releases](https://github.com/HatTapper/mc-settings-sync/releases) and run it.
Create a template root folder if you do not have one already, then
pick an instance and a template from the dropdowns. Once you're done, click **Apply
settings**. The application will display a prompt listing all of the changes that will
be applied. These changes **cannot be undone** after you accept, so make sure to review it carefully.

Both folder locations can be changed from the **Folders** section;
the choice is remembered in `%APPDATA%\mc-settings-sync\mc-settings-sync.json`.

The same executable also works from a terminal:

```bash
mc-settings-sync.exe "Fabric 1.21" fabric-sodium
```

The template name is optional and defaults to `base`. Pass `--dry-run` to list
what would be copied without writing anything. Note that the terminal form
applies immediately without the confirmation prompt, so use `--dry-run` first
if you are unsure.

## Roadmap

Planned features are:
- [Create Template From Instance](https://github.com/HatTapper/mc-settings-sync/issues/1): Allow users to create a template folder from an existing launcher instance by picking
  the files they would like to be carried over to the template
- [Version Mismatch Warning](https://github.com/HatTapper/mc-settings-sync/issues/2): Utilize files like Prism's `mmc-pack.json` to detect version mismatches and warn the user before applying
- [Wider Launcher Support](https://github.com/HatTapper/mc-settings-sync/issues/3): Extend functionality to support more launchers besides just Prism Launcher

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

To build the executable the same way CI does:

```bash
pyinstaller --noconfirm --onefile --windowed --name mc-settings-sync --icon assets/icon.ico --add-data "assets/icon.ico;assets" --paths src launcher.py
```

`launcher.py` exists because PyInstaller runs its entry script without a parent
package, which breaks the package's relative imports. It imports
`mc_settings_sync` by absolute name instead.

Every push runs the tests and builds the `.exe` on Windows; pushing a `v*` tag
also attaches the executable to a GitHub Release.

## License

MIT — see [LICENSE](LICENSE).
