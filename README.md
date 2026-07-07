# ftimgc — File to IMG Converter

A lightweight, fullscreen desktop application for Linux that converts any file to the `.img` format by renaming/copying it with a `.img` extension. Built with Python and Tkinter, styled with a modern dark theme.

---

## Screenshot

> _The app launches fullscreen with a built-in file browser, selection sidebar, progress bar, and convert button._

---

## Features

- **Fullscreen file browser** — navigate your filesystem with a clean, dark-themed tree view
- **Multi-file selection** — select multiple files at once using standard click/ctrl-click
- **Selection sidebar** — see all queued files before converting
- **Progress bar** — tracks conversion progress in real time
- **Threaded conversion** — UI stays responsive during conversion
- **Error reporting** — failed conversions are reported individually without stopping the batch
- **Keyboard shortcuts** — `Escape` to exit fullscreen, `F11` to re-enter fullscreen

---

## Requirements

- Python 3.8+
- Tkinter (usually bundled with Python; on Debian/Ubuntu install with `sudo apt install python3-tk`)

---

## Installation

### Run directly

```bash
git clone https://github.com/matthewglandi-arch/ftimgc.git
cd ftimgc
python3 converter.py
```

### Install via .deb package (Debian/Ubuntu)

A prebuilt `.deb` package is included in the repository:

```bash
sudo dpkg -i ftimgc_1.0.0_all.deb
```

After installation, **ftimgc** will appear in your application menu, or you can launch it from the terminal:

```bash
ftimgc
```

---

## Usage

1. Launch the app — it opens fullscreen automatically.
2. Browse to the folder containing the files you want to convert.
3. Click files to select them (multiple selections supported). Selected files appear in the sidebar on the right.
4. Click **⚙ Convert to .img** in the bottom bar.
5. The converted `.img` files are saved in the same directory as the originals.
6. A summary dialog confirms success or lists any errors.

To deselect all files, click **Clear Selection** in the sidebar.

---

## How It Works

ftimgc copies each selected file to a new path with the `.img` extension (using `shutil.copy2`, which preserves metadata). The original file is left untouched. This makes the tool useful for scenarios where software expects a raw `.img` file regardless of the underlying format.

---

## Project Structure

```
ftimgc/
├── converter.py          # Main application source
├── ftimgc.desktop        # Desktop entry file
├── ftimgc_1.0.0_all.deb  # Prebuilt Debian package
├── deb/                  # Debian package source tree
│   ├── DEBIAN/control
│   └── usr/
│       ├── bin/          # Installed binary
│       └── share/
│           ├── applications/ftimgc.desktop
│           └── ftimgc/converter.py
├── README.md
└── LICENSE
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
