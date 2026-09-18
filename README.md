# Pixel Forge

A self-contained sprite and animation editor for GitHub Pages. The application lives entirely in `index.html`: no build step, external libraries, account, API key, or backend is required.

## Use

Open `index.html` in a modern desktop browser. Start with the included crystal animation, choose **New** for a blank canvas, or choose **Generate** for an editable procedural sprite. Duplicate frames to animate and press **Space** to play.

**Save** downloads a lossless editable project. **Export** produces finished artwork. Keep downloaded project backups; browser-local recovery is not a substitute for saving.

## Features

- Pencil, eraser, flood fill, eyedropper, lines, rectangles, ellipses, brush opacity, and symmetry.
- Layers with visibility, locking, opacity, blend modes, reordering, duplication, and merge-down.
- Rectangular selections, move, copy, cut, paste, crop, flips, rotation, outlines, recoloring, and palette mapping.
- Animation timeline, per-frame timing, onion skin, loop/ping-pong/once playback, and live/tiled previews.
- Six procedural sprite recipes and motion-loop generation from existing artwork.
- Image import and sprite-sheet slicing; PNG, GIF, APNG, sprite sheets with JSON metadata, and PNG-frame ZIP exports.
- Undo/redo, keyboard shortcuts, zoom/pan, grid, and a collapsible inspector.

Generation is procedural, not text-to-image AI. Animated image imports currently become one decoded still; use sprite sheets or project files to import timelines. Canvases are limited to 256 x 256 pixels, with frame/layer limits and memory safeguards.

## GitHub Pages

In this repository's **Settings > Pages**, choose **Deploy from a branch**, select **main**, choose **/(root)**, and save.

After a successful Pages deployment, the site address is:

https://generalgroovy.github.io/sprites/

The `.nojekyll` file marks this as a plain static site. No package installation or build command is needed.

## Verification

The uploaded editor should have this SHA-256 checksum:

```text
2249003fce634c5df6ab60deba70d9fb7c60936755ae575d246b05345f1cacc3  index.html
```

The supplied release previously reported 61 passing automated checks in Chromium with embedded HTML rendering. That does not establish real-origin storage behavior, cross-browser support, physical touch-device behavior, or successful GitHub Pages deployment. Check those separately for your environment.
