"""Pixel Forge regression suite. Python 3 + playwright + Pillow. No app dependencies.
Run: python tests/regression.py --embedded
Omit --embedded to serve a real local origin and also check IndexedDB recovery.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image, ImageSequence
import argparse, base64, copy, io, json, random, threading, http.server, zipfile, zlib, struct, sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tests'/'artifacts';OUT.mkdir(exist_ok=True)
parser=argparse.ArgumentParser();parser.add_argument('--embedded',action='store_true');parser.add_argument('--chromium',default='/usr/bin/chromium');args=parser.parse_args()
RESULTS=[]
def test(name,fn):
    try:
        fn();RESULTS.append({'name':name,'pass':True});print('PASS',name,flush=True)
    except Exception as e:
        RESULTS.append({'name':name,'pass':False,'error':str(e)});print('FAIL',name,str(e)[:500],flush=True)
def check(value,message='Assertion failed'):
    if not value:raise AssertionError(message)
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
    def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as pw:
    launch={'headless':True,'args':['--no-sandbox','--disable-dev-shm-usage']}
    if Path(args.chromium).exists():launch['executable_path']=args.chromium
    browser=pw.chromium.launch(**launch)
    page=browser.new_page(viewport={'width':1440,'height':960},accept_downloads=True)
    page.set_default_timeout(4000)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    if args.embedded:page.set_content((ROOT/'index.html').read_text())
    else:page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
    page.wait_for_function('!!window.PixelForge');page.wait_for_timeout(200)
    for result in page.evaluate('PixelForge.runSelfTests()'):RESULTS.append(result)
    print('Internal tests:',len(RESULTS),flush=True)
    def state():return page.evaluate('PixelForge.getState()')
    def project():return page.evaluate('PixelForge.getProject()')
    def load(p):page.evaluate('(p)=>PixelForge.loadProject(p)',p);page.wait_for_timeout(40)
    def blank(w=16,h=16):
        p=page.evaluate('([w,h])=>PixelForge.createProject(w,h,"Regression")',[w,h]);load(p);return p
    def pixels(p=None,fi=0,li=None):
        p=p or project();li=li or p['layers'][0]['id'];return bytearray(base64.b64decode(p['frames'][fi]['cels'][li]))
    def pixel(x,y,p=None,fi=0,li=None):
        p=p or project();b=pixels(p,fi,li);i=(y*p['width']+x)*4;return tuple(b[i:i+4])
    def point(x,y):
        return page.evaluate('''([x,y])=>{const r=document.getElementById('editorCanvas').getBoundingClientRect(),s=PixelForge.getState(),p=PixelForge.getProject();return {x:r.left+Math.round((r.width-p.width*s.zoom)/2+s.panX)+(x+.5)*s.zoom,y:r.top+Math.round((r.height-p.height*s.zoom)/2+s.panY)+(y+.5)*s.zoom}}''',[x,y])
    def clickpix(x,y,button='left'):
        p=point(x,y);page.mouse.click(p['x'],p['y'],button=button)
    def dragpix(a,b):
        start=point(*a);end=point(*b);page.mouse.move(start['x'],start['y']);page.mouse.down();page.mouse.move(end['x'],end['y'],steps=12);page.mouse.up()
    def setvalue(id,value,event='change'):
        page.evaluate('([id,value,event])=>{const e=document.getElementById(id);e.value=value;e.dispatchEvent(new Event(event,{bubbles:true}))}',[id,str(value),event])
    def color(c):setvalue('hexColor',c)
    def tool(t):page.locator('[data-tool='+t+']').click()
    def undo():page.locator('#undoBtn').click()
    def confirm():page.locator('#modalSubmit').click()
    def png_pillow(data):return Image.open(io.BytesIO(data)).convert('RGBA')
    def export(options):
        result=page.evaluate('''async opts=>{const r=await PixelForge.export(opts),a=new Uint8Array(await r.blob.arrayBuffer());let s='';for(let i=0;i<a.length;i+=8192)s+=String.fromCharCode(...a.subarray(i,i+8192));return {name:r.name,data:btoa(s)}}''',options)
        data=base64.b64decode(result['data']);(OUT/result['name']).write_bytes(data);return data
    def pencil_test():
        blank();tool('pencil');color('#ff0000');dragpix((2,2),(10,2));p=project();check(sum(pixels(p)[3::4])==9*255);check(pixel(6,2)==(255,0,0,255));undo();check(not any(pixels()));page.locator('#redoBtn').click();check(pixel(6,2)==(255,0,0,255))
    test('UI pencil interpolation, undo and redo',pencil_test)
    def erase_test():
        tool('eraser');clickpix(6,2);check(pixel(6,2)[3]==0);undo();check(pixel(6,2)[3]==255)
    test('UI eraser is undoable',erase_test)
    def secondary_test():
        tool('pencil');setvalue('bgColor','#0000ff','input');clickpix(3,5,'right');check(pixel(3,5)==(0,0,255,255));tool('picker');clickpix(3,5);check(page.locator('#hexColor').input_value()=='#0000FF')
    test('Secondary color and eyedropper',secondary_test)
    def alpha_test():
        blank();tool('pencil');color('#ff0000');setvalue('brushOpacity',50,'input');dragpix((3,3),(8,3));check(pixel(5,3)[3]==128);setvalue('brushOpacity',100,'input')
    test('Brush alpha is applied once per gesture',alpha_test)
    def fill_test():
        blank(12,12);tool('rect');color('#ff0000');page.locator('#filledShape').uncheck();dragpix((2,2),(9,9));tool('fill');color('#0000ff');clickpix(5,5);check(pixel(5,5)==(0,0,255,255));check(pixel(0,0)[3]==0);check(pixel(2,4)==(255,0,0,255))
    test('Pixel rectangle and bounded flood fill',fill_test)
    def symmetry_test():
        blank();tool('pencil');color('#123456');page.locator('#mirrorX').check();page.locator('#mirrorY').check();clickpix(2,3);check(all(pixel(x,y)==(18,52,86,255) for x,y in [(2,3),(13,3),(2,12),(13,12)]));page.locator('#mirrorX').uncheck();page.locator('#mirrorY').uncheck()
    test('Two-axis symmetry reflects actual pixels',symmetry_test)
    def symmetric_fill_alpha_test():
        blank();tool('fill');color('#ff0000');setvalue('brushOpacity',50,'input');page.locator('#mirrorX').check();page.locator('#mirrorY').check();clickpix(2,3);check(all(a==128 for a in pixels()[3::4]),'Reflected fill should apply alpha once');page.locator('#mirrorX').uncheck();page.locator('#mirrorY').uncheck();setvalue('brushOpacity',100,'input')
    test('Symmetric flood fill does not compound partial alpha',symmetric_fill_alpha_test)
    def selection_test():
        blank();tool('pencil');color('#ff0000');clickpix(3,4);tool('select');dragpix((2,3),(5,6));check(state()['selection']=={'x':2,'y':3,'w':4,'h':4});page.locator('#selCopy').click();tool('move');page.locator('#editorCanvas').focus();page.keyboard.press('ArrowRight');check(pixel(4,4)==(255,0,0,255) and pixel(3,4)[3]==0);undo();check(pixel(3,4)[3]==255);page.locator('#selCut').click();check(not any(pixels()));page.locator('#selPaste').click();check(pixel(3,4)[3]==255)
    test('Selection, copy, move, cut, paste and undo',selection_test)
    def cancel_test():
        blank();tool('pencil');color('#ffffff');a=point(2,2);b=point(8,8);page.mouse.move(**a);page.mouse.down();page.mouse.move(**b);page.keyboard.press('Escape');page.mouse.up();check(not any(pixels()))
    test('Escape rolls back an active brush gesture',cancel_test)
    def locked_test():
        blank();page.locator('.layer.active button[title="Lock layer"]').click();tool('pencil');clickpix(4,4);check(not any(pixels()));page.locator('.layer.active button[title="Unlock layer"]').click();page.locator('.layer.active button[title="Hide layer"]').click();clickpix(4,4);check(not any(pixels()));page.locator('.layer.active button[title="Show layer"]').click()
    test('Locked and hidden layers reject drawing',locked_test)
    def frames_test():
        blank();tool('pencil');color('#aabbcc');clickpix(3,3);page.locator('#dupFrameBtn').click();check(len(project()['frames'])==2);clickpix(4,4);p=project();check(pixel(4,4,p,0)[3]==0 and pixel(4,4,p,1)[3]==255);setvalue('frameDuration',170);check(project()['frames'][1]['duration']==170);page.locator('#addFrameBtn').click();check(not any(pixels(project(),2)));setvalue('fpsInput',20);page.locator('#applyFpsBtn').click();check(all(f['duration']==50 for f in project()['frames']))
    test('Independent frame duplication, blank frames and timing',frames_test)
    def reorder_test():
        before=[f['id'] for f in project()['frames']];page.locator('.frame').nth(0).drag_to(page.locator('.frame').nth(2));after=[f['id'] for f in project()['frames']];check(after==[before[1],before[2],before[0]])
    test('Timeline drag-to-reorder preserves frame identities',reorder_test)
    def layer_test():
        page.locator('#dupLayerBtn').click();p=project();check(len(p['layers'])==2);check(all(f['cels'][p['layers'][0]['id']]==f['cels'][p['layers'][1]['id']] for f in p['frames']));page.locator('#mergeLayerBtn').click();check(len(project()['layers'])==1);page.locator('#addLayerBtn').click();check(len(project()['layers'])==2 and not any(pixels(project(),0,project()['layers'][1]['id'])))
    test('Layer duplication, merge-down and blank layer',layer_test)
    def transforms_test():
        blank(8,8);tool('pencil');color('#ff0000');clickpix(2,3);page.locator('#adjustTab').click();page.locator('[data-transform=flipX]').click();check(pixel(5,3)[3]==255 and pixel(2,3)[3]==0);page.locator('[data-transform=rotate]').click();check(pixel(4,5)[3]==255);undo();undo();check(pixel(2,3)[3]==255);page.locator('#paintTab').click()
    test('Flip and 90-degree rotation are pixel exact and undoable',transforms_test)
    def resize_test():
        page.locator('#adjustTab').click();page.locator('#resizeBtn').click();setvalue('resizeW',16);setvalue('resizeH',16);setvalue('resizeMode','scale');confirm();check(project()['width']==16);check(pixel(4,6)[3]==255 and pixel(5,7)[3]==255);undo();check(project()['width']==8);page.locator('#paintTab').click()
    test('Nearest-neighbor project resize and undo',resize_test)
    def crop_test():
        tool('select');dragpix((1,1),(5,5));page.locator('#adjustTab').click();page.locator('#cropBtn').click();confirm();check(project()['width']==5 and project()['height']==5);check(pixel(1,2)[3]==255);undo();page.locator('#paintTab').click()
    test('Crop all cels to selection',crop_test)
    def generation_test():
        blank(32,32);page.locator('#generateTab').click();page.locator('[data-recipe=robot]').click();setvalue('genFrames',8,'input');page.locator('#generateBtn').click();confirm();p=project();check(len(p['frames'])==8 and len(p['layers'])==3);check(p['frames'][0]['cels']!=p['frames'][2]['cels']);page.locator('#paintTab').click()
    test('Generator UI creates editable multi-layer animation',generation_test)
    def playback_test():
        setvalue('loopMode','once');setvalue('fpsInput',30);page.locator('#applyFpsBtn').click();page.locator('#playBtn').click();page.wait_for_timeout(600);check(not state()['playing'] and state()['activeFrame']==7);setvalue('loopMode','pingpong');page.locator('#playBtn').click();page.wait_for_timeout(150);check(state()['playing']);page.locator('#playBtn').click();check(not state()['playing'])
    test('Once playback stops; ping-pong runs and pauses',playback_test)
    def motion_test():
        page.locator('#adjustTab').click();setvalue('motionFrames',6);page.locator('#motionBtn').click();confirm();check(len(project()['frames'])==6);undo();check(len(project()['frames'])==8);page.locator('#paintTab').click()
    test('Motion-loop generator preserves undo',motion_test)
    def input_hotkey_test():
        tool('pencil');page.locator('#projectName').fill('bveg');page.locator('#projectName').press('Tab');check(state()['tool']=='pencil' and project()['name']=='bveg')
    test('Typing into inputs does not activate shortcuts',input_hotkey_test)
    def tab_keyboard_test():
        before=project();page.locator('#paintTab').focus();page.keyboard.press('ArrowRight');check(page.locator('#generateTab').get_attribute('aria-selected')=='true');check(project()==before,'Tab navigation must not nudge artwork');page.locator('#paintTab').click()
    test('Accessible inspector tab navigation does not alter pixels',tab_keyboard_test)
    # Import a real PNG and a real padded sprite sheet via file input.
    img=Image.new('RGBA',(12,8),(0,0,0,0));img.paste((255,40,0,255),(1,1,7,6));img.save(OUT/'import-fixture.png')
    sheet=Image.new('RGBA',(18,6),(0,0,0,0))
    for i,col in enumerate([(255,0,0,255),(0,255,0,255),(0,0,255,255)]):sheet.paste(col,(1+i*6,1,5+i*6,5))
    sheet.save(OUT/'sheet-fixture.png')
    def import_image_test():
        page.locator('#fileInput').set_input_files(OUT/'import-fixture.png');page.wait_for_selector('#importMode');setvalue('importMode','project');confirm();check(project()['width']==12 and project()['height']==8);check(pixel(2,2)==(255,40,0,255))
    test('Real PNG image import',import_image_test)
    def import_sheet_test():
        page.locator('#fileInput').set_input_files(OUT/'sheet-fixture.png');page.wait_for_selector('#importMode');setvalue('importMode','sheet');setvalue('importW',4,'input');setvalue('importH',4,'input');setvalue('sheetMargin',1,'input');setvalue('sheetGap',2,'input');confirm();p=project();check(len(p['frames'])==3 and p['width']==4);check([pixel(2,2,p,i) for i in range(3)]==[(255,0,0,255),(0,255,0,255),(0,0,255,255)])
    test('Padded sprite-sheet slicing and frame colors',import_sheet_test)
    # Restore a nontrivial, semitransparent animation for independent export tests.
    fixture=page.evaluate("PixelForge.generate('crystal',8,{primary:'#69d9b3',accent:'#c9f5e6',seed:42,motion:65},32,32)")
    fixture['name']='crystal-demo';fixture['frames'][2]['duration']=170;load(fixture)
    framezip=export({'format':'frames','scale':1})
    with zipfile.ZipFile(io.BytesIO(framezip)) as z:
        sourceframes=[png_pillow(z.read(n)) for n in sorted(z.namelist()) if n.endswith('.png')]
    def png_test():
        data=export({'format':'png','scale':3});im=png_pillow(data);check(im.size==(96,96));check(im.tobytes()==sourceframes[0].resize((96,96),Image.Resampling.NEAREST).tobytes())
    test('PNG export decodes and scales pixel-exactly',png_test)
    def apng_test():
        data=export({'format':'apng'});im=Image.open(io.BytesIO(data));check(im.n_frames==8 and im.info['loop']==0);durations=[]
        for i,frame in enumerate(ImageSequence.Iterator(im)):
            durations.append(frame.info['duration']);check(frame.convert('RGBA').tobytes()==sourceframes[i].tobytes(),f'RGBA mismatch frame {i}')
        check(durations[2]==170)
    test('APNG independent decode: all pixels, alpha, timing and loop',apng_test)
    def gif_test():
        data=export({'format':'gif'});im=Image.open(io.BytesIO(data));check(im.n_frames==8);durations=[]
        for i,frame in enumerate(ImageSequence.Iterator(im)):
            rgba=frame.convert('RGBA');expected=bytearray(sourceframes[i].tobytes());actual=rgba.tobytes()
            for k in range(0,len(expected),4):
                if expected[k+3]<128:check(actual[k+3]==0,f'Alpha mismatch {i}/{k}')
                else:check(actual[k:k+3]==expected[k:k+3] and actual[k+3]==255,f'Color mismatch {i}/{k}')
            durations.append(frame.info['duration'])
        check(durations[2]==170)
    test('GIF independent decode: exact small palette, transparency and timing',gif_test)
    def sheet_export_test():
        data=export({'format':'sheet','scale':2,'columns':3,'padding':2});z=zipfile.ZipFile(io.BytesIO(data));check(z.testzip() is None);meta=json.loads(z.read('crystal-demo-atlas.json'));im=png_pillow(z.read('crystal-demo-sheet.png'));check(im.size==(204,204));check(meta['frames'][4]['frame']=={'x':70,'y':70,'w':64,'h':64});check(im.crop((70,70,134,134)).tobytes()==sourceframes[4].resize((64,64),Image.Resampling.NEAREST).tobytes())
    test('Sprite sheet ZIP integrity, atlas coordinates and cell pixels',sheet_export_test)
    def pingpong_export_test():
        p=copy.deepcopy(fixture);p['loop']='pingpong';load(p);gif=Image.open(io.BytesIO(export({'format':'gif'})));apng=Image.open(io.BytesIO(export({'format':'apng'})));check(gif.n_frames==14 and apng.n_frames==14)
    test('Ping-pong GIF and APNG encode forward-and-back order',pingpong_export_test)
    def once_export_test():
        p=copy.deepcopy(fixture);p['loop']='once';load(p);gif=Image.open(io.BytesIO(export({'format':'gif'})));apng=Image.open(io.BytesIO(export({'format':'apng'})));check('loop' not in gif.info and apng.info['loop']==1)
    test('Once-only exports do not request infinite looping',once_export_test)
    def fallback_png_test():
        page.evaluate('()=>{window.__compressionBackup=window.CompressionStream;window.CompressionStream=undefined;}');data=export({'format':'png'});check(png_pillow(data).tobytes()==sourceframes[0].tobytes());page.evaluate('()=>{window.CompressionStream=window.__compressionBackup;}')
    test('PNG stored-deflate fallback decodes losslessly',fallback_png_test)
    # Stress every LZW code-width boundary and dictionary resets with independent decoding.
    for ncolors in [2,3,16,128,255]:
        def lzw_test(ncolors=ncolors):
            p=page.evaluate('PixelForge.createProject(128,128,"lzw-stress")');rng=random.Random(540+ncolors);palette=[(i,(i*47)%256,(i*71)%256,255) for i in range(ncolors)];data=bytearray()
            for i in range(128*128):data.extend(palette[rng.randrange(ncolors)])
            p['frames'][0]['cels'][p['layers'][0]['id']]=base64.b64encode(data).decode();load(p);encoded=export({'format':'gif'});decoded=png_pillow(encoded);check(decoded.tobytes()==bytes(data),f'{ncolors}-color LZW mismatch')
        test(f'GIF LZW dictionary growth/reset: {ncolors} opaque colors',lzw_test)
    def quantization_test():
        p=page.evaluate('PixelForge.createProject(64,64,"palette-stress")');data=bytearray()
        for y in range(64):
            for x in range(64):data.extend((x*4,y*4,(x+y)*2,255))
        p['frames'][0]['cels'][p['layers'][0]['id']]=base64.b64encode(data).decode();load(p);decoded=png_pillow(export({'format':'gif'}));actual=decoded.tobytes();error=sum(abs(data[i]-actual[i]) for i in range(len(data)) if i%4<3)/(64*64*3);check(error<12,f'Mean channel error {error}')
    test('Adaptive GIF palette quantization: 4096-color gradient',quantization_test)
    def actual_download_test():
        load(fixture)
        with page.expect_download() as download:
            page.locator('#saveBtn').click()
        saved=download.value;target=OUT/saved.suggested_filename;saved.save_as(target);p=json.loads(target.read_text());check(p['format']=='pixel-forge' and p['frames']==fixture['frames'])
        with page.expect_download() as download:
            page.locator('#exportBtn').click();setvalue('exportFormat','gif');confirm()
        target=OUT/download.value.suggested_filename;download.value.save_as(target);check(Image.open(target).n_frames==8)
    test('Real Save and GIF Export button downloads',actual_download_test)
    def malicious_import_test():
        p=copy.deepcopy(fixture);p['layers'][0]['id']='__proto__';before=project();bad=OUT/'invalid.json';bad.write_text(json.dumps(p));page.locator('#fileInput').set_input_files(bad);page.wait_for_timeout(150);check(project()==before and not page.locator('#modal').is_visible())
    test('Invalid project import is rejected without mutation',malicious_import_test)
    def responsiveness_test():
        page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(150);check(page.evaluate('document.documentElement.scrollWidth')==390,'Horizontal overflow');check(state()['zoom']<=8,'Canvas did not refit');page.screenshot(path=str(OUT/'mobile-final.png'));page.locator('#propertiesBtn').click();page.wait_for_timeout(150);check(page.locator('#inspector').is_visible());page.screenshot(path=str(OUT/'mobile-panels-final.png'));page.locator('#propertiesBtn').click();page.set_viewport_size({'width':1440,'height':960});page.wait_for_timeout(100);page.screenshot(path=str(OUT/'desktop-final.png'))
    test('390px responsive layout, auto-fit and mobile inspector',responsiveness_test)
    if not args.embedded:
        def recovery_test():
            before=project();check(page.evaluate('PixelForge.saveLocal()'));page.reload();page.wait_for_function('window.PixelForge&&PixelForge.getState().storageReady');page.wait_for_timeout(150);check(project()==before)
        test('Actual IndexedDB autosave and reload restoration',recovery_test)
    test('No uncaught browser exceptions',lambda:check(not errors,str(errors)))
    print('Browser:',browser.version)
    browser.close()
server.shutdown()
report={'passed':sum(r['pass'] for r in RESULTS),'total':len(RESULTS),'embedded':args.embedded,'errors':errors,'tests':RESULTS,'limitations':['Firefox, Safari and real touch hardware not tested.']+(['Navigation policy required embedded HTML rendering; real-origin IndexedDB restoration not exercised.'] if args.embedded else [])}
(OUT/'regression-report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='tests'},indent=2));sys.exit(0 if all(r['pass'] for r in RESULTS) else 1)
