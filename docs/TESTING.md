# Verification — Pixel Forge 1.1.0

Tested on 18 September 2026 in **Chromium 144.0.7559.96**, headless, using Python Playwright and embedded HTML rendering.

| Suite | Result | Scope |
| --- | --- | --- |
| `tests/regression.py --embedded` | **61 / 61 passed** | Existing editor operations, project validation, generators, animation, real downloads, and independently decoded exports. |
| `tests/workbench.py --embedded` | **32 / 32 passed** | Action search, keyboard navigation, context hints, disabled commands, non-drag reordering, timing dialog, views, documentation UI and responsive layout. |

**93 / 93 checks passed. No uncaught browser exceptions were recorded.** The workbench suite recorded no external application requests.

## Specific checks

Core coverage includes drawing and erasing, fill, shapes, symmetry, selection, cut/copy/paste, independent frames/layers, timing, Undo/Redo, transforms, resize/crop, procedural generation and playback. PNG, GIF and APNG outputs were decoded with Pillow; ZIP archives and atlas coordinates were inspected independently. Real Save and Export button downloads were exercised.

Workbench coverage verifies Ctrl+K filtering, Enter execution, arrow navigation, Escape dismissal, safe typing, no-result handling and visibly disabled commands. Frame-reorder actions preserve IDs and support Undo. The FPS dialog applies an explicit value. Hold bars and time totals track actual frame duration.

PNG output bytes, project JSON and Undo count were compared before and after changing canvas surfaces, rulers, grid and onion skin. They remained identical. Focus mode expands the canvas without editing artwork. A panel action restores the inspector. The Save indicator clears on a real editable-project download.

Reduced-motion emulation freezes automatic recipe previews while preserving user-requested playback. Help opens with the basic workflow and expands reference sections. Quick-start buttons open actual creation flows.

Responsive checks passed at **1920×1080, 1440×960, 1280×720, 1024×768, 820×740, 800×600, 390×844, 320×640 and 667×375**. Checks cover document overflow, visible file controls and non-collapsed canvas/timeline. The mobile properties drawer was opened, closed and reached through action search. These are browser viewport tests, not physical-device tests.

## Not established by these results

This environment blocks browser navigation to localhost with `ERR_BLOCKED_BY_ADMINISTRATOR`, so the final runs used `--embedded`. They do **not** establish real-origin IndexedDB persistence, successful live Pages deployment, Firefox/Safari compatibility, physical touchscreen behavior, complete accessibility conformance or performance on every supported device.

The test scripts support normal local-origin runs; the core suite additionally checks save/reload restoration when `--embedded` is omitted. See [Development](DEVELOPMENT.md#test) for commands.

## Tested artifact

```text
7e3a11a991dad6fec1ecc7b089d0cf525504d813e16a3da865d87bb57744d8dc  index.html
```

Tests and this report belong to this revision. Re-run them after changing the editor; do not carry the counts forward without verification.
