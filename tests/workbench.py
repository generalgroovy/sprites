"""Browser checks for the workbench UI. Does not require a build step.
Run: python tests/workbench.py [--embedded] [--chromium /path/to/chromium]
Artifacts are written to tests/artifacts/ and intentionally ignored by Git.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import argparse, http.server, json, threading, sys
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tests' / 'artifacts'
OUT.mkdir(exist_ok=True)
parser = argparse.ArgumentParser()
parser.add_argument('--embedded', action='store_true', help='Render HTML without navigation; skips origin/storage verification.')
parser.add_argument('--chromium', default='/usr/bin/chromium')
args = parser.parse_args()
results, errors, requests = [], [], []

def check(condition, message='Assertion failed'):
    if not condition:
        raise AssertionError(message)

def test(name, fn):
    try:
        fn()
        results.append({'name': name, 'pass': True})
        print('PASS', name, flush=True)
    except Exception as exc:
        results.append({'name': name, 'pass': False, 'error': str(exc)})
        print('FAIL', name, str(exc)[:350], flush=True)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)
    def log_message(self, *a):
        pass

server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
with sync_playwright() as pw:
    launch = {'headless': True, 'args': ['--no-sandbox', '--disable-dev-shm-usage']}
    if Path(args.chromium).exists():
        launch['executable_path'] = args.chromium
    browser = pw.chromium.launch(**launch)
    page = browser.new_page(viewport={'width': 1440, 'height': 960}, accept_downloads=True)
    page.set_default_timeout(3000)
    page.on('pageerror', lambda exc: errors.append(str(exc)))
    page.on('request', lambda req: requests.append(req.url))
    if args.embedded:
        page.set_content((ROOT / 'index.html').read_text())
    else:
        page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
    page.wait_for_function('!!window.PixelForge')
    page.wait_for_timeout(200)
    fixture = page.evaluate('PixelForge.getProject()')
    def state():
        return page.evaluate('PixelForge.getState()')
    def project():
        return page.evaluate('PixelForge.getProject()')
    def reset():
        if page.locator('#modal').is_visible():
            page.locator('#modalCancel').click()
        page.evaluate('(p) => PixelForge.loadProject(p)', fixture)
    def search(query, execute=False):
        page.locator('#commandsBtn').click()
        page.locator('#commandSearch').fill(query)
        if execute:
            page.locator('#commandSearch').press('Enter')
    def export_bytes():
        return page.evaluate('async()=>Array.from(new Uint8Array(await (await PixelForge.export({format:"png"})).blob.arrayBuffer()))')
    def control_value(id, value):
        page.locator('#' + id).fill(str(value))
        page.locator('#' + id).dispatch_event('change')

    test('Version and initialization', lambda: check(page.evaluate('PixelForge.version') == '1.1.0'))
    def tool_hints():
        page.locator('[data-tool=move]').click()
        check('Arrows: 1 pixel' in page.locator('#contextHint').inner_text())
        page.locator('[data-tool=pencil]').click()
        check('Alt: sample' in page.locator('#contextHint').inner_text())
    test('Tool selection updates relevant guidance', tool_hints)
    def locked_hint():
        page.locator('.layer.active button[title="Lock layer"]').click()
        check('Layer locked' in page.locator('#contextHint').inner_text())
        page.locator('.layer.active button[title="Unlock layer"]').click()
    test('Locked layer guidance explains why painting is blocked', locked_hint)
    def finder_keyboard():
        page.locator('#editorCanvas').focus()
        page.keyboard.press('Control+k')
        check(page.locator('#commandSearch').evaluate('(e)=>e===document.activeElement'))
        page.locator('#commandSearch').fill('onion')
        check(page.locator('#commandResults button').count() == 1)
        before = page.locator('#onionBtn').get_attribute('aria-pressed')
        page.locator('#commandSearch').press('Enter')
        check(not page.locator('#modal').is_visible())
        check(page.locator('#onionBtn').get_attribute('aria-pressed') != before)
    test('Ctrl+K searches and runs an action with Enter', finder_keyboard)
    def no_results():
        before = project()
        search('zznonexistentzz')
        check(page.locator('#commandResults button').count() == 0)
        check('No matching' in page.locator('#commandCount').inner_text())
        page.locator('#commandSearch').press('Enter')
        check(page.locator('#modal').is_visible() and project() == before)
        page.keyboard.press('Escape')
    test('No-match search is explanatory and Enter is harmless', no_results)
    def search_navigation():
        search('frame')
        page.locator('#commandSearch').press('ArrowDown')
        check(page.evaluate('document.activeElement.closest("#commandResults") !== null'))
        page.keyboard.press('ArrowUp')
        check(page.locator('#commandSearch').evaluate('(e)=>e===document.activeElement'))
        page.keyboard.press('Escape')
    test('Action finder supports arrow navigation and Escape', search_navigation)
    def typing_safe():
        before = state()['tool']
        search('bvegimo')
        check(state()['tool'] == before)
        page.keyboard.press('Escape')
    test('Typing a search never invokes drawing shortcuts', typing_safe)
    def action_disabled():
        reset()
        search('crop selection')
        check(page.locator('#commandResults button').count() == 1)
        check(page.locator('#commandResults button').is_disabled())
        page.keyboard.press('Escape')
    test('Unavailable commands are visibly disabled', action_disabled)
    def layer_command():
        reset()
        n = len(project()['layers'])
        search('add layer', True)
        check(len(project()['layers']) == n + 1)
        page.locator('#undoBtn').click()
        check(len(project()['layers']) == n)
    test('Layer actions share existing undoable engine operations', layer_command)
    def keyboard_reorder():
        reset()
        before = [f['id'] for f in project()['frames']]
        search('move frame later', True)
        check([f['id'] for f in project()['frames']] == [before[1], before[0]] + before[2:])
        check(state()['activeFrame'] == 1)
        page.locator('#undoBtn').click()
        check([f['id'] for f in project()['frames']] == before)
    test('Non-drag frame reorder preserves identities and supports Undo', keyboard_reorder)
    def fps_command():
        reset()
        before = [f['duration'] for f in project()['frames']]
        search('set animation fps', True)
        check(page.locator('#fpsDialogValue').is_visible())
        page.locator('#fpsDialogValue').fill('20')
        page.locator('#modalSubmit').click()
        check(all(f['duration'] == 50 for f in project()['frames']))
        page.locator('#undoBtn').click()
        check([f['duration'] for f in project()['frames']] == before)
    test('Searchable FPS dialog sets explicit timing and is undoable', fps_command)
    def duration_meters():
        reset()
        control_value('frameDuration', 300)
        values = page.locator('.hold-meter').evaluate_all('(els)=>els.map(e=>parseFloat(e.style.getPropertyValue("--hold")))')
        check(values[0] == 100 and 33 < values[1] < 34)
        check('1.00 s' in page.locator('#timelineSummary').inner_text())
        page.locator('#undoBtn').click()
    test('Hold meters reflect real durations; timeline total stays current', duration_meters)
    def view_isolation():
        reset()
        before, bytes_before, undo_before = project(), export_bytes(), state()['undo']
        for surface in ['paper', 'dark', 'checker']:
            page.locator('#canvasSurface').select_option(surface)
            check(state()['canvasSurface'] == surface)
            check(export_bytes() == bytes_before)
        page.locator('#rulersBtn').click()
        page.locator('#gridBtn').click()
        page.locator('#onionBtn').click()
        check(export_bytes() == bytes_before and project() == before and state()['undo'] == undo_before)
        page.locator('#rulersBtn').click()
        page.locator('#gridBtn').click()
        page.locator('#onionBtn').click()
    test('Surfaces, rulers, grid and onion skin do not change PNG bytes, project or Undo', view_isolation)
    def surface_color():
        blank = page.evaluate('PixelForge.createProject(16,16,"Background check")')
        page.evaluate('(p)=>PixelForge.loadProject(p)', blank)
        page.locator('#canvasSurface').select_option('paper')
        page.wait_for_timeout(60)
        rgba = page.evaluate('()=>{const c=document.getElementById("editorCanvas");return Array.from(c.getContext("2d").getImageData(c.width/2,c.height/2,1,1).data)}')
        check(rgba == [238, 232, 216, 255], str(rgba))
        page.locator('#canvasSurface').select_option('checker')
        reset()
    test('Paper surface renders without painting the document', surface_color)
    def focus_view():
        before, undo_before = project(), state()['undo']
        width = page.locator('#stage').bounding_box()['width']
        page.locator('#focusBtn').click()
        page.wait_for_timeout(70)
        check(page.locator('#stage').bounding_box()['width'] > width)
        check(not page.locator('#inspector').is_visible())
        check(project() == before and state()['undo'] == undo_before)
        search('generate a sprite', True)
        page.wait_for_timeout(70)
        check(page.locator('#inspector').is_visible() and page.locator('#generatePanel').is_visible())
        check(not state()['focusWorkspace'])
        page.locator('#paintTab').click()
    test('Focus mode expands canvas; panel action restores inspector without edits', focus_view)
    def save_indicator():
        reset()
        control_value('frameDuration', 200)
        check(page.locator('#saveBtn').get_attribute('data-modified') == 'true')
        with page.expect_download() as dl:
            page.locator('#saveBtn').click()
        dl.value.save_as(OUT / 'workbench-backup.spriteforge.json')
        check(page.locator('#saveBtn').get_attribute('data-modified') == 'false')
        check(json.loads((OUT / 'workbench-backup.spriteforge.json').read_text()) == project())
        reset()
    test('Backup indicator clears on actual project download', save_indicator)
    def help_sections():
        page.locator('#helpBtn').click()
        check(page.locator('.help-section').count() == 3)
        check(page.locator('.help-section[open]').count() == 0)
        page.locator('.help-section summary').first.click()
        check(page.locator('.format-guide').is_visible())
        check('Recovery is not a backup' in page.locator('#modalBody').inner_text())
        page.keyboard.press('Escape')
    test('Help starts with a workflow and expands export/reference details', help_sections)
    def reduced_motion():
        page.emulate_media(reduced_motion='reduce')
        page.locator('#generateTab').click()
        page.wait_for_timeout(40)
        before = page.locator('#generatorPreview').evaluate('(c)=>c.toDataURL()')
        page.wait_for_timeout(300)
        check(page.locator('#generatorPreview').evaluate('(c)=>c.toDataURL()') == before)
        page.locator('#paintTab').click()
        page.locator('#playBtn').click()
        page.wait_for_timeout(200)
        check(state()['playing'] and page.locator('#playState').inner_text() == 'PLAYING')
        page.locator('#playBtn').click()
        page.emulate_media(reduced_motion='no-preference')
    test('Reduced-motion freezes recipe autoplay but respects deliberate playback', reduced_motion)
    def unique_ids():
        ids = page.locator('[id]').evaluate_all('(els)=>els.map(e=>e.id)')
        check(len(ids) == len(set(ids)))
        names = page.locator('button:not([hidden])').evaluate_all('els=>els.filter(e=>{const r=e.getBoundingClientRect();return r.width&&r.height&&!e.getAttribute("aria-label")&&!e.getAttribute("title")&&!e.textContent.trim()}).map(e=>e.id)')
        check(not names, str(names))
    test('Controls have labels; element IDs remain unique', unique_ids)
    # Fit the same editable document on large, small, portrait and landscape viewports.
    for width, height in [(1920,1080),(1440,960),(1280,720),(1024,768),(820,740),(800,600),(390,844),(320,640),(667,375)]:
        def responsive(width=width, height=height):
            page.set_viewport_size({'width': width, 'height': height})
            page.wait_for_timeout(100)
            check(page.evaluate('document.documentElement.scrollWidth') == width, 'Page overflow')
            check(page.locator('#stage').bounding_box()['height'] > 35, 'Drawing stage collapsed')
            check(page.locator('#frames').bounding_box()['height'] >= 65, 'Timeline collapsed')
            check(page.locator('#commandsBtn').is_visible() and page.locator('#exportBtn').is_visible())
            # Visible file controls must stay within the viewport, not merely be clipped.
            for id in ['newBtn', 'openBtn', 'saveBtn', 'commandsBtn', 'exportBtn']:
                r=page.locator('#'+id).bounding_box()
                check(r['x'] >= 0 and r['x']+r['width'] <= width+1, id + ' outside viewport')
            if width in [1440,390,320,667]:
                page.screenshot(path=str(OUT / f'workbench-{width}x{height}.png'))
        test(f'Responsive workspace {width} × {height}', responsive)
    def mobile_drawer():
        page.set_viewport_size({'width':390,'height':844})
        page.wait_for_timeout(100)
        page.locator('#propertiesBtn').click()
        check(page.locator('#inspector').is_visible())
        check(page.locator('#closePanelsBtn').is_visible())
        page.locator('#closePanelsBtn').click()
        page.wait_for_timeout(180)
        check(not page.locator('#inspector').is_visible())
        search('generate a sprite',True)
        check(page.locator('#inspector').is_visible() and page.locator('#generatePanel').is_visible())
        page.locator('#closePanelsBtn').click()
    test('Mobile drawer opens, closes, and deep-links from command search', mobile_drawer)
    def quick_start():
        page.set_viewport_size({'width':1440,'height':960})
        page.wait_for_timeout(100)
        page.locator('#paintTab').click()
        page.locator('#quickRecipeBtn').click()
        check(page.locator('#generatePanel').is_visible())
        page.locator('#paintTab').click()
        page.locator('#quickNewBtn').click()
        check(page.locator('#newWidth').is_visible())
        page.keyboard.press('Escape')
    test('Quick-start buttons open working creation flows', quick_start)
    test('No external application requests', lambda:check(not [r for r in requests if not r.startswith(('http://127.0.0.1:','data:','blob:'))],str(requests)))
    test('No uncaught browser exceptions', lambda:check(not errors,str(errors)))
    reset()
    page.locator('#paintTab').click()
    page.locator('.inspector-content').evaluate('e=>e.scrollTop=0')
    page.locator('#fitBtn').click()
    page.wait_for_timeout(100)
    page.locator('#toast').evaluate('e=>e.classList.remove("show")')
    page.screenshot(path=str(OUT / 'workbench-desktop.png'))
    page.locator('#generateTab').click()
    page.wait_for_timeout(100)
    page.screenshot(path=str(OUT / 'workbench-generator.png'))
    page.locator('#paintTab').click()
    search('frame')
    page.screenshot(path=str(OUT / 'workbench-actions.png'))
    page.keyboard.press('Escape')
    page.locator('#helpBtn').click()
    page.screenshot(path=str(OUT / 'workbench-help.png'))
    version=browser.version
    browser.close()
server.shutdown()
report={'passed':sum(r['pass'] for r in results),'total':len(results),'browser':'Chromium '+version,'embedded':args.embedded,'errors':errors,'tests':results,'limitations':['Firefox, Safari, physical touch devices and real-origin recovery are not verified by embedded rendering.']}
(OUT / 'workbench-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='tests'},indent=2))
sys.exit(0 if all(r['pass'] for r in results) else 1)
