# Development

[Overview](../README.md) · [Verification report](TESTING.md)

## Run

The complete runtime is `index.html`: HTML, CSS, icons, JavaScript and encoders are embedded. There is no build process and no remote runtime dependency. Opening the file directly works; a local HTTP server provides a conventional origin for recovery testing:

```sh
python -m http.server 8000
```

Open `http://localhost:8000`. Use GitHub Pages' branch/root publishing for deployment.

## Change the right layer

CSS begins with layout primitives, followed by the commented **WORKBENCH 1.1** visual rules and responsive layouts. Amber identifies editing selections; blue identifies motion. Keep neutral backgrounds around the artwork, clear focus outlines, labels for icon buttons, and reduced-motion support. Do not encode selection or playback state using color alone.

JavaScript is divided by comments into utilities, project/history, rendering, drawing, editor actions, recipes, persistence, import, exporters, UI and diagnostics. The **WORKBENCH GUIDANCE & VIEW CONTROLS** section owns action search, hints, ruler drawing, canvas surfaces and focus mode.

`window.PixelForge` exposes the version, project/state snapshots, validation-backed loading, generators, exports and self-tests for diagnostics and automation. Project JSON remains format version **1**; the interface version is **1.1.0**.

Preserve these invariants:

- Each frame owns an independent RGBA cel for every layer. Layer properties are shared tracks.
- Project mutations use the existing `edit` / snapshot / Undo path. View changes do not change pixel data, serialization, revision history or exported composites.
- `renderMain` draws guides; `composite` supplies artwork to exports. Never bake interface surfaces or guides into project cels.
- Action search delegates to the same guarded editor operations as visible controls. Disabled operations must stay disabled; destructive actions keep their confirmations.
- Keep import validation, memory budgets and recovery error handling. Recovery never substitutes for a downloaded project.

## Test

Python is used only for development tests. The editor itself needs no Python packages.

```sh
python -m pip install -r tests/requirements.txt
python -m playwright install chromium
python tests/regression.py
python tests/workbench.py
```

Both scripts use `/usr/bin/chromium` when present, otherwise Playwright's installed Chromium. Override it with `--chromium /path/to/chromium`. Each script creates its own local HTTP server.

For environments that block navigation to localhost, append `--embedded`. That renders the same HTML but does **not** verify real-origin IndexedDB recovery. Tests write JSON reports, downloads and screenshots to the ignored `tests/artifacts/` directory. Failures return a nonzero exit code.

Before release, also test real-origin recovery, a Pages deployment, Firefox, Safari, keyboard-only operation and a physical touch device. The current report identifies what was actually exercised rather than treating these as already verified.

Update `SHA256SUMS.txt` after modifying `index.html`:

```sh
python -c "import hashlib,pathlib; p=pathlib.Path('index.html'); pathlib.Path('SHA256SUMS.txt').write_text(hashlib.sha256(p.read_bytes()).hexdigest()+'  index.html\n')"
```
