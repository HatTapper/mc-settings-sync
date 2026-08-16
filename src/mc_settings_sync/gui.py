import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.messagebox import QUESTION as ICON_QUESTION, WARNING as ICON_WARNING

from .paths import Settings, list_instances, list_templates
from .sync import SyncError, SyncResult, apply_template

# ui padding
PAD = 8

# folders where an overwrite costs real progress rather than just a setting
RISKY_DIRS = {"saves", "mods", "resourcepacks", "shaderpacks", "screenshots"}


class App(ttk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=PAD)

        self.settings = Settings.load()
        self.grid(sticky="nsew")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.instance_var = tk.StringVar()
        self.template_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready.")

        self._build()
        self.refresh()

    def _build(self) -> None:
        row = 0

        ttk.Label(self, text="Instance").grid(row=row, column=0, sticky="w", pady=(0, PAD))
        self.instance_box = ttk.Combobox(
            self, textvariable=self.instance_var, state="readonly"
        )
        self.instance_box.grid(row=row, column=1, sticky="ew", padx=(PAD, 0), pady=(0, PAD))

        row += 1
        ttk.Label(self, text="Template").grid(row=row, column=0, sticky="w", pady=(0, PAD))
        self.template_box = ttk.Combobox(
            self, textvariable=self.template_var, state="readonly"
        )
        self.template_box.grid(row=row, column=1, sticky="ew", padx=(PAD, 0), pady=(0, PAD))

        row += 1
        paths = ttk.LabelFrame(self, text="Folders", padding=PAD)
        paths.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, PAD))
        paths.columnconfigure(1, weight=1)

        self.instances_label = ttk.Label(paths, text="", wraplength=380)
        self.templates_label = ttk.Label(paths, text="", wraplength=380)

        ttk.Label(paths, text="Instances").grid(row=0, column=0, sticky="w")

        self.instances_label.grid(row=0, column=1, sticky="w", padx=PAD)
        ttk.Button(paths, text="Change…", command=self.pick_instances_root).grid(row=0, column=2)
        ttk.Label(paths, text="Templates").grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.templates_label.grid(row=1, column=1, sticky="w", padx=PAD, pady=(4, 0))
        ttk.Button(paths, text="Change…", command=self.pick_templates_root).grid(
            row=1, column=2, pady=(4, 0)
        )

        row += 1
        buttons = ttk.Frame(self)
        buttons.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, PAD))
        ttk.Button(buttons, text="Refresh", command=self.refresh).pack(side="left")
        ttk.Button(buttons, text="Apply settings", command=self.apply).pack(side="right")

        row += 1
        ttk.Label(self, textvariable=self.status_var, wraplength=460).grid(
            row=row, column=0, columnspan=2, sticky="w"
        )

    def refresh(self) -> None:
        instances = list_instances(self.settings.instances_root)
        templates = list_templates(self.settings.templates_root)

        self._fill(self.instance_box, self.instance_var, instances)
        self._fill(self.template_box, self.template_var, templates)

        self.instances_label.config(text=str(self.settings.instances_root))
        self.templates_label.config(text=str(self.settings.templates_root))

        if not instances:
            self.set_status(f"No instances found in {self.settings.instances_root}", error=True)
        elif not templates:
            self.set_status(f"No templates found in {self.settings.templates_root}", error=True)
        else:
            self.set_status(f"{len(instances)} instance(s), {len(templates)} template(s).")

    @staticmethod
    def _fill(box: ttk.Combobox, var: tk.StringVar, values: list[str]) -> None:
        box["values"] = values
        if var.get() not in values:
            var.set(values[0] if values else "")

    def pick_instances_root(self) -> None:
        self._pick("instances_root", "Select the Prism instances folder")

    def pick_templates_root(self) -> None:
        self._pick("templates_root", "Select the templates folder")

    def _pick(self, attr: str, title: str) -> None:
        chosen = filedialog.askdirectory(title=title, initialdir=str(getattr(self.settings, attr)))
        if chosen:
            setattr(self.settings, attr, Path(chosen))
            self.settings.save()
            self.refresh()

    def apply(self) -> None:
        instance = self.instance_var.get()
        template = self.template_var.get()

        if not instance or not template:
            self.set_status("Pick both an instance and a template first.", error=True)
            return

        # dry run first so the confirmation can say exactly what is about to happen
        try:
            preview = apply_template(
                self.settings.instances_root,
                instance,
                self.settings.templates_root,
                template,
                dry_run=True,
            )
        except (SyncError, OSError) as exc:
            self.set_status(str(exc), error=True)
            return

        if preview.count == 0:
            self.set_status(f"Template '{template}' is empty, nothing copied.", error=True)
            return

        if not self._confirm(instance, template, preview):
            self.set_status("Cancelled, nothing was copied.")
            return

        try:
            result = apply_template(
                self.settings.instances_root,
                instance,
                self.settings.templates_root,
                template,
            )
        except (SyncError, OSError) as exc:
            self.set_status(str(exc), error=True)
            return

        if result.count == 0:
            self.set_status(f"Template '{template}' is empty, nothing copied.", error=True)
        else:
            self.set_status(
                f"Copied {result.count} file(s) from '{template}' into '{instance}'."
            )

    # spells out what is about to be overwritten, and flags the folders worth worrying about
    def _confirm(self, instance: str, template: str, preview: SyncResult) -> bool:
        existing = [name for name in preview.copied if preview.destination.joinpath(name).exists()]
        risky = sorted({name.split("/")[0] for name in preview.copied} & RISKY_DIRS)

        lines = [
            f"Apply template '{template}' to instance '{instance}'?",
            "",
            f"{preview.count} file(s) will be written to:",
            str(preview.destination),
            "",
            f"{len(existing)} existing file(s) will be overwritten."
            if existing
            else "No existing files will be overwritten.",
        ]

        if risky:
            lines += [
                "",
                f"WARNING: this template writes into {', '.join(risky)}.",
                "That can replace worlds or mods in this instance.",
            ]

        lines += ["", "This cannot be undone.", "", self._file_list(preview.copied)]

        return messagebox.askokcancel(
            "Confirm apply",
            "\n".join(lines),
            icon=ICON_WARNING if risky else ICON_QUESTION,
        )

    @staticmethod
    def _file_list(names: list[str], limit: int = 15) -> str:
        shown = "\n".join(names[:limit])

        if len(names) > limit:
            shown += f"\n... and {len(names) - limit} more"

        return shown

    def set_status(self, message: str, error: bool = False) -> None:
        self.status_var.set(("Error: " if error else "") + message)


def main() -> int:
    root = tk.Tk()
    root.title("MC Settings Sync")
    root.minsize(520, 300)

    App(root)

    root.mainloop()
    return 0
