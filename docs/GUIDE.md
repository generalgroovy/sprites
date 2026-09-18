# Using Pixel Forge

[Back to the editor overview](../README.md)

## Create, draw, animate

Start with the example or **New**. Small canvases, such as 16 × 16 or 32 × 32, are useful for learning. **Open** accepts image files, sprite sheets and saved projects; dropping a file onto the workspace also imports it.

Choose a tool on the left and a color in **Paint**. Right-click uses the secondary color; hold **Alt** to sample. **Mirror X / Y** reflect strokes. Hold **Shift** to constrain shapes or lines. Shift-click with Pencil connects to the previous point.

**Duplicate frame** copies all layers into an independent frame. Change that pose and press **Space**. **Onion skin** shows the previous pose in red and the next in blue. It is an editing guide, not part of the artwork.

**Hold** is the selected frame's duration in milliseconds: 100 ms is one tenth of a second. **Set FPS** assigns the same duration to every frame and replaces individual holds. Search for “Set animation FPS” to set a value when the compact timeline hides that field. Changes are undoable.

Drag frames to reorder them, or search for **Move frame earlier / later**. Double-click a frame to name it or edit its hold. Loop, ping-pong and once control playback; animation exports use the selected mode. Sheets and frame ZIPs keep the original frame order.

## Work with layers and selections

Each frame contains independent pixels for each layer. Layer names, order, visibility, opacity and blend mode belong to the entire animation. Show and unlock a layer before painting. Double-click its name to rename it.

**Select (M)** draws a rectangle. Copy/cut/paste affect the active layer, using the editor's own pixel clipboard. **Move (V)** moves that selection, or the whole active cel when there is no selection. Arrow keys nudge one pixel; Shift+arrows nudge ten. Escape cancels a stroke or deselects.

**Crop selection** crops every frame and layer. **Resize canvas** can pad/crop or scale with nearest-neighbor sampling. Rotation stays within the selected bounds; non-square areas may clip.

## Generate a starting point

**Generate** includes Crystal, Slime, Flame, Robot, Orbit and Sapling. Choose colors, a seed, frame count and motion amount. The same parameters reproduce the same pixels. Set one frame for a still sprite.

Generation replaces the timeline with editable sprite, detail and shadow layers. It asks for confirmation; Undo restores the previous work. Save a project first to keep it permanently. There are no AI prompts or network generation services.

Under **Adjust → Make a motion loop**, float, bounce, shake, spin or pulse the current pose. Only the active layer moves; other layers stay still. This replaces the timeline and ignores a selection. It is also undoable.

## See the artwork clearly

Canvas **Checker / Dark / Paper** surfaces help inspect transparent or dark pixels. Rulers stay aligned with project coordinates while zooming and panning. Grid, rulers, onion skins, selection outlines and canvas surfaces never enter exports.

**Focus workspace** hides the inspector to enlarge the canvas. Tools and timeline remain available. Selecting a panel through **Find an action** restores it. On narrow screens, **Panels** opens properties, and the drawer has its own close button.

The live preview has independent scale, background and tiled-preview controls. Reduced-motion settings freeze automatic recipe previews; an animation you explicitly play still runs.

## Save and export

**Save** downloads a `.spriteforge.json` project with layers, frames, palette, timings and playback mode. Reopen it with **Open** to continue editing. The amber dot beside Save marks changes since the latest project download in this session; it is not proof that an earlier backup still exists.

Browser recovery is a convenience, not permanent storage. Its status explicitly says “Recovery saved” rather than implying that a file was downloaded. Use one editing tab per site and download backups regularly.

| Export | Best use | Important detail |
| --- | --- | --- |
| PNG | A single sprite | Current frame's visible composite. |
| Sprite sheet + atlas | Import into a game | ZIP includes PNG and JSON coordinates, names, timing and playback metadata. |
| GIF | Sharing an animation | Up to 255 opaque colors plus transparency; partial alpha is thresholded, timing rounds to 10 ms. |
| APNG | Full-color animation | Preserves RGBA, including partial transparency. |
| PNG frames | Another editing pipeline | ZIP includes individual frames and timing JSON. |

Pixel scale uses nearest-neighbor enlargement. Transparent exports remain transparent regardless of the canvas surface. Choose a solid export matte explicitly when needed. Hidden layers are omitted; layer opacity and blending are included. Save the editable project separately because image exports flatten the layers.

## Everyday shortcuts

Use Cmd instead of Ctrl on macOS. Shortcuts do not activate while typing in fields.

| Action | Key |
| --- | --- |
| Find an action | Ctrl+K |
| Pencil / eraser / fill / sample | B / E / G / I |
| Line / rectangle / ellipse | L / U / O |
| Select / move / pan | M / V / H |
| Play / pause | Space |
| Previous / next frame | , / . |
| Duplicate / blank frame | Alt+D / Alt+N |
| Undo / redo | Ctrl+Z / Ctrl+Shift+Z |
| Save / open / export | Ctrl+S / Ctrl+O / Ctrl+E |
| Select all / deselect | Ctrl+A / Escape |
| Copy / cut / paste | Ctrl+C / Ctrl+X / Ctrl+V |
| Fit / actual pixels | F / 1 |
| Zoom / brush size | + and − / [ and ] |
| Swap colors / onion skin / grid | X / Q / Ctrl+G |
| Help | ? or F1 |

Scroll zooms at the pointer; middle-drag pans. On touchscreens, use Pan and the zoom buttons. Multi-touch pinch is not implemented.

## Troubleshooting and limits

**Nothing draws:** check that the selected layer is visible and unlocked, check brush opacity, and clear any unintended selection. The status hint explains locked or hidden layers.

**A picture imports without animation:** animated GIF, WebP and PNG imports currently become one decoded still. Import a sprite sheet with the correct frame dimensions or open a saved project to get a timeline.

**An animation differs after export:** GIF reduces colors and alpha; use APNG for full RGBA. PNG exports only the current frame. Layer visibility and opacity affect exports; editor guides do not.

**Recovery is unavailable:** Save still downloads a project. Browser privacy settings, storage eviction, private browsing and site changes can affect recovery. Local files and the hosted page do not share recovery storage.

**A limit is reached:** canvases are 1–256 pixels per side; up to 128 frames and 16 layers share a 16 MB raw-pixel budget. Undo keeps up to 80 steps within an approximate 48 MB budget. Large exports are capped at 32 megapixels. Reduce dimensions, frames, layers or export scale.

Native Aseprite/PSD files, skeletal rigging, audio and video export are not supported.
