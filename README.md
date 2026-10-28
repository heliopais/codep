# codep ⚡️

> Instant macOS Spotlight & CLI launcher for your code projects and workspaces.

[![macOS](https://img.shields.io/badge/macOS-12%20%7C%2013%20%7C%2014%20%7C%2015-black.svg?logo=apple)](https://apple.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0-success.svg)](#zero-dependencies)

`codep` turns native macOS Spotlight (`⌘ Space`) into a parameterized project launcher that jumps directly into any project or workspace in your editor in less than a second.

No heavy background daemons, no Electron bloat, and zero external package dependencies—just pure native macOS speed.

---

## The Workflow

```text
⌘ Space  ➔  codep  ➔  Return  ➔  [type project name]  ➔  Return
```

1. Hit **`⌘ Space`**, type **`codep`** (or just `code`), and hit **`Return`**.
2. A lightweight prompt appears, immediately focused and ready for typing.
3. Type your project name (e.g., `mrt`, `benefits training`, `exo inference`) and press **`Return`**.
4. Your editor opens directly on that project folder.

---

## Features

- **⚡️ Zero-Click Focus Bypass:** Uses native macOS `AppKit` (`activateIgnoringOtherApps:true`) to bypass window focus-stealing prevention. When launched from Spotlight, the prompt snaps frontmost and accepts keystrokes immediately.
- **🧠 Multi-Token Path Intelligence:** Searches both folder names and repository hierarchy. For example, typing `"benefits training"` immediately matches `~/repos/benefits/benefits-model-training`.
- **🎯 Instant Single-Winner Launch:** Unambiguous or exact matches skip confirmation dialogs and launch your editor instantly.
- **🪄 "Did You Mean...?" Fuzzy Fallback:** Typos and approximate searches (e.g. `"benifits train"`) automatically present the closest ranked options with the top candidate pre-selected.
- **💻 CLI Companion:** Includes a terminal command (`codep <query>`) so you can jump into projects directly from your shell.
- **🎨 Multi-Editor Support:** Works out of the box with **Visual Studio Code**, **Cursor**, **Zed**, **VSCodium**, **Windsurf**, or any editor of your choice.
- **🪶 Zero Dependencies:** Built strictly using native AppleScript and the macOS Python standard library. No `brew`, `pip`, or `npm` installs required.

---

## Installation

Clone the repository and run the installer:

```bash
git clone https://github.com/heliopais/codep.git
cd codep
make install
```

The installer will:
1. Compile the native Cocoa-focused launcher to `~/Applications/codep.app`.
2. Automatically locate and attach your editor's official icon.
3. Symlink `bin/codep` to `~/.local/bin/codep` for command-line access.
4. Notify macOS LaunchServices to index the new app in Spotlight immediately.

---

## Configuration (Optional)

`codep` works out of the box with sensible defaults (`~/repos`, `~/Documents`, `~/Projects`, `~/Developer`, `~/Code`).

To customize search roots or your preferred editor, create `~/.config/codep/config.json`:

```json
{
  "editor": "Visual Studio Code",
  "search_roots": [
    "~/repos",
    "~/Documents",
    "~/Developer"
  ],
  "ignored_dirs": [
    ".git", ".venv", "venv", "node_modules", "dist", "build", "site-packages"
  ],
  "max_depth": 3
}
```

### Supported Editors
Change `"editor"` in `config.json` (or set `CODEP_EDITOR`) to any installed editor name:
- `"Visual Studio Code"` *(default)*
- `"Cursor"`
- `"Zed"`
- `"VSCodium"`
- `"Windsurf"`

---

## Terminal Usage

You can also use `codep` straight from your shell:

```bash
# Jump directly to a project
codep mrt

# Multi-token search
codep "benefits training"

# Open the native GUI prompt
codep

# List all discovered project directories
codep --list
```

---

## Architecture

```text
[ Spotlight (⌘ Space) ]  or  [ Terminal (codep <query>) ]
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│ launcher.applescript (Cocoa AppKit)                        │
│ 1. Forces frontmost focus bypassing Spotlight animation     │
│ 2. Prompts user for project query or path                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ resolver.py (Python stdlib)                                │
│ 1. Scans search roots up to configured max_depth            │
│ 2. Filters noisy folders (.venv, node_modules, .git)        │
│ 3. Scores multi-token matches & fuzzy similarity            │
│ 4. Returns: SINGLE | MULTIPLE | APPROX                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Result Handler                                              │
│ • SINGLE:   Directly executes: open -a <Editor> <Path>      │
│ • MULTIPLE: Shows native disambiguation list                │
│ • APPROX:   Shows "Did you mean...?" suggestions           │
└─────────────────────────────────────────────────────────────┘
```

---

## Development & Testing

Run the automated test suite:

```bash
make test
```

---

## License

[MIT](LICENSE) © [Helio Pais](https://github.com/heliopais)
