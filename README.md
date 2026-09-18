# Pixel Forge

**A pixel-art and animation workbench in one HTML file.** Draw sprites, build frame-by-frame animations, or start from an editable procedural recipe. Your artwork stays in your browser. No installation, account, external library or API key is required.

[Open the editor](https://generalgroovy.github.io/sprites/) · [User guide](docs/GUIDE.md) · [Development & tests](docs/DEVELOPMENT.md)

## Make your first animation

1. Edit the crystal example, choose **New** for a blank canvas, or use **Generate** for a recipe.
2. Pick a color and draw. **Duplicate frame**, change the pose, then press **Space** to preview.
3. **Save** downloads an editable project. **Export** makes finished artwork. Keep both.

**Find an action** (`Ctrl/Cmd+K`) searches tools, panels, timing, imports and exports. The **?** help button explains the workflow and shortcuts inside the editor. On narrow screens, use **Panels** for colors, layers and generators.

## What is where?

| Area | Use it for |
| --- | --- |
| Tool rail | Drawing, erasing, filling, sampling, shapes, selection and movement. |
| Canvas | Pixel editing, zoom, grid, onion skin and coordinate rulers. Checker / Dark / Paper surfaces are view-only. |
| Motion strip | Frames, per-frame holds, playback, duplication and reordering. Hold bars compare each duration with the longest frame. |
| Paint | Colors, palettes and layers. Layer visibility, opacity and order apply across all frames. |
| Generate | Six seeded, editable sprite recipes. This is procedural generation, not AI. |
| Adjust | Transforms, color changes, canvas resizing and motion loops from a pose. |

**Amber marks editing selections; blue marks playback.** Focus mode gives the canvas more room without hiding the timeline or tools.

## Choose an export

**PNG** for one sprite. **GIF** for convenient sharing. **APNG** for full-color animation with partial transparency. **Sprite sheet + JSON** for games. **PNG frames + timing JSON** for another editor.

**Browser recovery is not a backup.** Download project files regularly; storage is browser- and site-specific and may be cleared. Use one editing tab per site.

## Run or publish

Open `index.html` directly, or serve this folder with `python -m http.server 8000`. No build command is needed.

For the editor link above, enable **Settings → Pages → Deploy from a branch → main → /(root)** in this repository. Keep `.nojekyll` in the root. Deployment settings are separate from the editor code.

Canvas sizes are **1–256 pixels per side**, with a **16 MB raw-pixel budget**, up to **128 frames** and **16 layers**. Animated image imports become one still; use a sprite sheet or saved project for a timeline. [Details and troubleshooting](docs/GUIDE.md#troubleshooting-and-limits).

## Verification

Version **1.1.0**: **61 core checks + 32 workbench checks passed** in Chromium using embedded HTML rendering, including export decoding and 320–1920 px layouts. Real-origin recovery, live Pages deployment, Firefox, Safari and physical touch hardware were not verified by these runs. See the [test report](docs/TESTING.md) for exact scope and reproduction commands.
