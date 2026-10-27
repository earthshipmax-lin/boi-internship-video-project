#!/usr/bin/env python3
"""Independent browser/encoded QA for the provisional 603-frame people study.

Run from any directory. --partial permits still-only coverage and skips media.
--qa-dir selects the isolated study directory (default: visual-study-r04).
Only this verifier and derived QA files are authored by this reviewer.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import math
import re
import subprocess

V = Path(__file__).resolve().parents[1]
Q = V / 'qa/v13/people/visual-study-r04'
LOCALES = ['yue', 'en', 'zh-CN']
LEADS = ['david-lau', 'patrick-li', 'pamela-cheng', 'manli-chan', 'ken-yeung', 'david-wang']
PARTNERS = ['lily-ku', 'noah-cheung', 'catherine-luo', 'vivian-mau', 'crystal-wang']
N = 603


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def run(args):
    return subprocess.check_output(args, text=True)


def probe(p):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_entries',
                          'format=duration,size:stream=codec_type,codec_name,width,height,avg_frame_rate,nb_frames',
                          '-of', 'json', str(p)]))


def overlap(a, b, tolerance=.1):
    return (min(a['x'] + a['width'], b['x'] + b['width']) - max(a['x'], b['x']) > tolerance and
            min(a['y'] + a['height'], b['y'] + b['height']) - max(a['y'], b['y']) > tolerance)


def inside(r, left=0, top=0, right=1920, bottom=1080, eps=.2):
    return (r['x'] >= left - eps and r['y'] >= top - eps and
            r['x'] + r['width'] <= right + eps and r['y'] + r['height'] <= bottom + eps)


def filter_amount(css, name, default):
    """Read the computed CSS filter value; absent filters use their identity."""
    if not isinstance(css, str):
        return None
    match = re.search(r'\b'+re.escape(name)+r'\(\s*([+\-\d.eE]+)(%?)\s*\)',css)
    return float(match[1])/(100 if match[2] else 1) if match else default


def curve(x):
    x = max(0, min(1, x))
    if x in [0, 1]:
        return x
    def cubic(t, a, b):
        return 3 * (1-t)**2 * t * a + 3 * (1-t) * t*t * b + t**3
    lo, hi = 0, 1
    for _ in range(48):
        m = (lo + hi) / 2
        if cubic(m, .16, .3) < x:
            lo = m
        else:
            hi = m
    return cubic((lo + hi)/2, 1, 1)


def expected_phase(f):
    if f < 60:
        return 'opening', -1, f
    if f < 492:
        return 'person', (f-60)//72, (f-60)%72
    if f < 507:
        return 'return', 5, f-492
    if f < 513:
        return 'exit', 5, f-507
    return 'wall', -1, f-513


def caption_id(phase, index):
    if phase == 'opening':
        return 'opening'
    if phase == 'wall':
        return 'partner-wall'
    return ['david-lau', 'patrick-li', 'operations-compliance', 'operations-compliance',
            'hong-kong-new-york', 'hong-kong-new-york'][index]


CAPTIONS = {
    'yue': ['平台嘅高度，由人嚟決定。', '三十年跨國企業經驗，帶領集團看得更遠。',
            '精算嘅嚴謹，令每一份方案經得起時間。', '由營運到合規，每一個環節，都有人把關。',
            '由香港到紐約，同一份專業，同一份承諾。', '一群人，一個方向：守護每一個家族嘅未來。'],
    'en': ['A platform rises as high as its people.', 'Thirty years with global firms, leading the group to see further.',
           'Actuarial rigour that lets every plan stand the test of time.',
           'From operations to compliance, every step has a guardian.',
           'From Hong Kong to New York, one standard, one promise.',
           "Many people, one purpose: safeguarding every family's future."],
    'zh-CN': ['平台的高度，由人来决定。', '三十年跨国企业经验，带领集团看得更远。',
              '精算的严谨，让每一份方案经得起时间。', '从营运到合规，每一个环节，都有人把关。',
              '从香港到纽约，同一份专业，同一份承诺。', '一群人，一个方向：守护每一个家族的未来。'],
}
CAPTION_KEYS = ['opening', 'david-lau', 'patrick-li', 'operations-compliance', 'hong-kong-new-york', 'partner-wall']


def main(partial=False):
    Q.mkdir(exist_ok=True, parents=True)
    failures, checks, range_overlaps, coverage = [], 0, [], {}
    stats = {'max_native_scale': 0, 'max_eye_error_px': 0, 'max_photo_width_error_px': 0,
             'min_visible_photo_text_gap_px': float('inf'), 'min_merits_caption_gap_px': float('inf'),
             'min_font_box_photo_gap_px': float('inf'), 'min_font_box_caption_gap_px': float('inf'),
             'min_computed_saturation':float('inf'),'max_computed_saturation':0,
             'max_computed_grayscale':0,'max_effective_photo_opacity_error':0,
             'max_observed_merits_lines': 0}

    def ck(ok, locale, frame, rule, evidence=None):
        nonlocal checks
        checks += 1
        if not ok:
            failures.append({'locale': locale, 'frame': frame, 'rule': rule, 'evidence': evidence})

    for locale in LOCALES:
        source = Q / f'{locale}-all-frames.json'
        if partial and not source.exists():
            source = Q / f'{locale}-stills.json'
        if not source.exists():
            coverage[locale] = {'source': None, 'frames': 0, 'complete': False}
            if not partial:
                ck(False, locale, None, 'full browser audit exists')
            continue
        raw = json.loads(source.read_text())
        rows = list(raw.values()) if isinstance(raw, dict) else raw
        frames = [a['frame'] for a in rows]
        complete = sorted(frames) == list(range(N))
        coverage[locale] = {'source': str(source), 'sha256': sha(source), 'frames': len(rows),
                            'complete': complete, 'missing': sorted(set(range(N))-set(frames))}
        name_geometry = {}
        ck(len(frames) == len(set(frames)), locale, None, 'unique browser frame records')
        if not partial:
            ck(complete, locale, None, 'all603 frames covered', len(frames))
        for row in rows:
            f = row['frame']; phase, index, local = expected_phase(f)
            ck(row['locale'] == locale and row['totalFrames'] == N and row['visualStudy'] is True,
               locale, f, 'same provisional study and locale')
            ck((row['phase'], row['index'], row['local']) == (phase, index, local),
               locale, f, 'one-pass phase order matches603frame schedule')
            ck(row['root'] == {'width': 1920, 'height': 1080}, locale, f, 'native1920x1080 root')
            photos = row['photos']; lead = [p for p in photos if p['kind'] == 'lead']
            if phase != 'wall':
                ck([p['id'] for p in lead] == LEADS, locale, f, 'six original leads in fixed order')
                widths = [p['rect']['width'] for p in lead]
                total_width = sum(widths) + 5*8
                stats['max_photo_width_error_px'] = max(stats['max_photo_width_error_px'], abs(total_width-1660))
                ck(abs(total_width-1660) <= 1, locale, f, 'actual DOM lead widths plus gaps equal1660', total_width)
                ck(all(abs(w-round(w)) <= .02 for w in widths), locale, f, 'all card widths are integer pixels', widths)
                ck(abs(lead[0]['rect']['x']-130) <= .02 and
                   abs(lead[-1]['rect']['x']+lead[-1]['rect']['width']-1790) <= .02,
                   locale, f, 'photo row spans130..1790')
                ck(all(abs(b['rect']['x']-a['rect']['x']-a['rect']['width']-8) <= .02
                       for a, b in zip(lead, lead[1:])), locale, f, 'every photo gap is8px')
                ck(row['photoTotalWidth'] == 1660 and row['photoRight'] == 1790,
                   locale, f, 'declared row agrees with actual DOM geometry')
                p = curve((local-6)/15) if phase == 'person' else curve(local/15) if phase == 'return' else 1
                ck(abs(row['progress']-p) <= 1e-8, locale, f, 'CSS cubic inversion agrees with independent curve')
                old = [270]*6 if phase != 'person' or index == 0 else [900 if i == index-1 else 144 for i in range(6)]
                new = [900 if i == index else 144 for i in range(6)] if phase == 'person' else [270]*6
                if phase == 'return':
                    old = [900 if i == 5 else 144 for i in range(6)]
                for i, photo in enumerate(lead):
                    expected_focus = p if phase == 'person' and i == index else (1-p if phase == 'person' and i == index-1 else 0)
                    if phase == 'return': expected_focus = 1-p if i == 5 else 0
                    if phase in ['opening', 'exit']: expected_focus = 0
                    ck(abs(photo['focus']-expected_focus) <= 1e-8, locale, f, 'only scheduled incoming/outgoing focus changes', photo['id'])
                    ck(abs(photo['motionScale']-(1.04-.04*photo['focus'])) < 1e-9,
                       locale, f, 'photo zoom shares the same focus progress', photo['id'])
                    if phase in ['person', 'return']:
                        expected_width = old[i] + (new[i]-old[i])*p
                        ck(abs(photo['rect']['width']-expected_width) <= 1.001,
                           locale, f, 'actual rounded width agrees with shared curve', {'id':photo['id'],'actual':photo['rect']['width'],'float':expected_width})
            else:
                ck([p['id'] for p in photos] == PARTNERS, locale, f, 'five partners only on wall')
                ck(all(p['rect']['width'] == 300 and p['rect']['height'] == 400 for p in photos),
                   locale, f, 'partner portraits300x400')
            for photo in photos:
                b, raw_box = photo['rect'], photo['rawImage']
                expected_saturation=.55+.35*photo['focus']
                expected_opacity=.65+.35*photo['focus']
                image_filter=photo.get('computedImageFilter')
                actual_gray=filter_amount(image_filter,'grayscale',0)
                actual_sat=filter_amount(image_filter,'saturate',1)
                card_opacity=photo.get('computedCardOpacity')
                ck(image_filter is not None and card_opacity is not None,locale,f,
                   'computed image filter and card opacity are captured',photo['id'])
                ck(abs(photo['grayscale'])<1e-9 and actual_gray is not None and abs(actual_gray)<1e-9,
                   locale,f,'all lead and partner photos retain color: actual grayscale is always0',
                   {'id':photo['id'],'computed_filter':image_filter,'declared_grayscale':photo['grayscale']})
                ck(photo.get('saturation') is not None and abs(photo.get('saturation',0)-expected_saturation)<1e-9
                   and actual_sat is not None and abs(actual_sat-expected_saturation)<=1.5e-6,
                   locale,f,'declared and actual saturation share focus curve .55 to .90',
                   {'id':photo['id'],'declared':photo.get('saturation'),'computed':actual_sat,'expected':expected_saturation})
                ck(abs(photo['declaredOpacity']-expected_opacity)<1e-9 and card_opacity is not None
                   and abs(card_opacity-expected_opacity)<=1.5e-6,locale,f,
                   'declared and computed card opacity share focus curve .65 to1',
                   {'id':photo['id'],'declared':photo['declaredOpacity'],'computed':card_opacity,'expected':expected_opacity})
                if phase=='wall':
                    parent_opacity=curve((local-PARTNERS.index(photo['id'])*3)/9)
                else:
                    parent_opacity=curve(local/12) if phase=='opening' else 1-curve(local/6) if phase=='exit' else 1
                opacity_error=abs(photo['opacity']-expected_opacity*parent_opacity)
                ck(opacity_error<=2e-6,locale,f,'actual effective photo opacity includes only scheduled parent entrance/exit',
                   {'id':photo['id'],'actual':photo['opacity'],'expected':expected_opacity*parent_opacity})
                stats['max_effective_photo_opacity_error']=max(stats['max_effective_photo_opacity_error'],opacity_error)
                if actual_gray is not None:stats['max_computed_grayscale']=max(stats['max_computed_grayscale'],abs(actual_gray))
                if actual_sat is not None:
                    stats['min_computed_saturation']=min(stats['min_computed_saturation'],actual_sat)
                    stats['max_computed_saturation']=max(stats['max_computed_saturation'],actual_sat)
                ck(inside(b, 40, 40, 1880, 1040), locale, f, 'visible photo viewport within picture safe zone', photo['id'])
                ck(photo['clip'] == 'hidden', locale, f, 'raw image clipped by its own photo viewport', photo['id'])
                sx, sy = photo['nativeScaleX'], photo['nativeScaleY']
                stats['max_native_scale'] = max(stats['max_native_scale'], sx, sy)
                ck(max(sx, sy) <= 1.6001, locale, f, 'total native scale including zoom <=1.6', {'id':photo['id'],'x':sx,'y':sy})
                aspect_pixel_error = abs(raw_box['width'] - raw_box['height']*photo['nativeWidth']/photo['nativeHeight'])
                ck(aspect_pixel_error <= .1, locale, f, 'source aspect ratio preserved within CSS subpixel rounding', {'id':photo['id'],'width_error_px':aspect_pixel_error})
                e, target = photo['screenEye'], photo['targetEye']
                error = math.hypot(e['x']-target['x'], e['y']-target['y'])
                stats['max_eye_error_px'] = max(stats['max_eye_error_px'], error)
                ck(error <= 1, locale, f, 'manual source framing reference remains at card centre/upper third', {'id':photo['id'],'error':error})

            texts = [t for t in row['texts'] if t['opacity'] > .02 and t.get('glyphRect')]
            caption = next(t for t in row['texts'] if t['role'] == 'caption')
            expected_caption = CAPTIONS[locale][CAPTION_KEYS.index(caption_id(phase, index))]
            ck(caption['text'] == expected_caption, locale, f, 'caption uses unique source wording for visual phase')
            ck(caption['rect'] == {'x':105,'y':1018,'width':1710,'height':48}, locale, f, 'provisional caption box held fixed')
            ck(len(caption['glyphLines']) == 1, locale, f, 'caption is one actual DOM-wrapped line')
            for t in texts:
                ck(inside(t['glyphRect']), locale, f, 'visible glyph ink within1920x1080', t['role'])
                ck(t['scrollWidth'] <= t['clientWidth']+1, locale, f, 'text fits available width', t['role'])
                for photo in photos:
                    if photo['opacity'] <= .02: continue
                    ck(not overlap(t['glyphRect'], photo['rect']), locale, f, 'visible text glyphs do not overlap photo viewport', [t['role'],photo['id']])
                    if t['role'] in ['name','role','merits']:
                        gap = t['glyphRect']['y'] - photo['rect']['y']-photo['rect']['height']
                        if gap >= 0: stats['min_visible_photo_text_gap_px'] = min(stats['min_visible_photo_text_gap_px'], gap)
                size = float(t['fontSize'].replace('px',''))
                if t['role'] == 'name':
                    ck(36 <= size <= 44, locale, f, 'lead name remains36..44px', size)
                    expected_family = 'Source Serif 4' if locale == 'en' else 'Noto Serif TC'
                    ck(expected_family in t['fontFamily'], locale, f, 'lead name uses serif family', t['fontFamily'])
                    ck(len(t['glyphLines']) == 1, locale, f, 'lead name does not wrap')
                    measured=(size,t['fontRect']['width'],t['fontRect']['height'])
                    reference=name_geometry.setdefault(t['owner'],measured)
                    ck(all(abs(a-b)<.02 for a,b in zip(measured,reference)),locale,f,
                       'visible name font size and measured Range dimensions never scale',
                       {'owner':t['owner'],'actual':measured,'reference':reference})
                if t['role'] == 'role':
                    ck(18 <= size <= 20 and len(t['glyphLines']) == 1, locale, f,
                       'lead role remains18..20px on one line', size)
                if t['role'] == 'merits':
                    stats['max_observed_merits_lines'] = max(stats['max_observed_merits_lines'], len(t['glyphLines']))
                    ck(18 <= size <= 20 and len(t['glyphLines']) <= 2 and t['scrollHeight'] <= 53,
                       locale, f, 'three merit fragments fit at18..20px in at most2 lines', {'size':size,'lines':len(t['glyphLines']),'scrollHeight':t['scrollHeight']})
                    gap = caption['glyphRect']['y']-t['glyphRect']['y']-t['glyphRect']['height']
                    stats['min_merits_caption_gap_px'] = min(stats['min_merits_caption_gap_px'], gap)
                if t['role'].startswith('partner-'):
                    ck(phase == 'wall', locale, f, 'partner labels only during wall')
                    ck(size == (18 if t['role'] == 'partner-name' else 14), locale, f,
                       'partner label uses18px name or14px role', size)
                if t['role'] in ['name','role','merits','partner-name','partner-role']:
                    for photo in photos:
                        if photo['opacity'] <= .02: continue
                        for box_kind in ['rect','fontRect']:
                            ck(not overlap(t[box_kind],photo['rect']), locale, f,
                               'actual text element/font reserve stays outside photo viewport',
                               [t['role'],box_kind,photo['id']])
                        gap=t['fontRect']['y']-photo['rect']['y']-photo['rect']['height']
                        stats['min_font_box_photo_gap_px']=min(stats['min_font_box_photo_gap_px'],gap)
                    for box_kind in ['rect','fontRect']:
                        ck(not overlap(t[box_kind],caption[box_kind]), locale, f,
                           'actual text element/font reserve stays outside caption', [t['role'],box_kind])
                    gap=caption['fontRect']['y']-t['fontRect']['y']-t['fontRect']['height']
                    stats['min_font_box_caption_gap_px']=min(stats['min_font_box_caption_gap_px'],gap)
            if phase == 'wall':
                wall_labels=[t for t in row['texts'] if t['role'] in ['partner-name','partner-role']]
                ck(len(wall_labels)==10 and all(sum(t['owner']==p and t['role']==role for t in wall_labels)==1
                   for p in PARTNERS for role in ['partner-name','partner-role']),locale,f,
                   'partner wall has exactly one name and role per person')
                ck(not any(t['role'] in ['name','role','merits'] for t in row['texts']),locale,f,
                   'partner wall has no lead merits or extra labels')
            for a,b in itertools.combinations(texts, 2):
                ck(not overlap(a['glyphRect'], b['glyphRect']), locale, f, 'visible glyph ink boxes do not intersect', [a['role'],b['role']])
                if a['owner'] is not None and a['owner']==b['owner'] and set([a['role'],b['role']]) in [set(['name','role']),set(['role','merits'])]:
                    ck(not overlap(a['fontRect'],b['fontRect']),locale,f,
                       'same-owner name-role and role-merits Range font boxes do not intersect',
                       {'roles':[a['role'],b['role']],'owner':a['owner'],'fontRects':[a['fontRect'],b['fontRect']]})
                if overlap(a['fontRect'], b['fontRect']):
                    range_overlaps.append({'locale':locale,'frame':f,'roles':[a['role'],b['role']],
                                           'same_owner':a['owner']==b['owner'], 'glyph_overlap':overlap(a['glyphRect'],b['glyphRect'])})

    baseline = json.loads((V/'qa/v13/people/baseline.json').read_text())
    changed = [name for name,h in baseline.items() if not (V/name).exists() or sha(V/name) != h]
    ck(not changed, None, None, 'all original476 protected files unchanged', changed)
    old_us = V/'qa/v13/people/before/video/qa/us-v1/CURRENT_SELECTION.json'
    ck(sha(old_us) == sha(V/'qa/us-v1/CURRENT_SELECTION.json'), None, None, 'US current selection unchanged')
    all_complete = all(coverage.get(l,{}).get('complete') for l in LOCALES)
    status='partial_visual_study_QA_not_final' if partial else 'complete_browser_QA_media_pending' if all_complete and not failures else 'failed_browser_QA_not_final'
    result = {'status':status,
              'study_dir':str(Q),'script_sha256':sha(Path(__file__)),
              'passed':not failures,'checks':checks,'failure_count':len(failures),'failures':failures[:200],
              'coverage':coverage,'stats':stats,'range_font_box_overlaps':range_overlaps,
              'color_policy':{'user_update':'all photos retain color; nonfocus photos are weaker in color',
                              'grayscale':0,'saturation':'0.55+0.35*focus','card_opacity':'0.65+0.35*focus'},
              'range_font_box_overlap_count':len(range_overlaps),'protected_total':len(baseline),'protected_changed':changed,
              'limitations':['This is a603frame/20.1s silent layout study, not approved voice timing or a complete multilingual long film.',
                             'Canvas glyph bounds are based on browser font metrics for actual DOM-wrapped lines, not raster pixel segmentation.',
                             'Range font boxes include ascender/descender reserves; any overlaps are separately reported rather than described as zero.',
                             'Actual computed CSS image filters and card opacity are checked against the shared focus progress, including scheduled ancestor entrance/exit opacity; this is not independent per-pixel filter analysis.']}
    for k,v in list(stats.items()):
        if not math.isfinite(v): stats[k] = None
    suffix = '-partial' if partial else ''
    output = Q/f'verification{suffix}.json'
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    if not partial and not failures:
        try:
            result['media'] = verify_media()
            result['status']='complete_visual_study_QA'
        except (AssertionError, OSError, subprocess.CalledProcessError, StopIteration, KeyError) as e:
            result['passed']=False
            result['status']='failed_media_QA_not_final'
            failures.append({'locale':None,'frame':None,'rule':'all exported studies must probe and decode completely','evidence':str(e)})
            result['failure_count']=len(failures)
            result['failures']=failures[:200]
        output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        if not failures:write_report(result)
    print(json.dumps({k:result[k] for k in ['status','passed','checks','failure_count','stats','range_font_box_overlap_count']},ensure_ascii=False))
    return 0 if not failures else 1


def verify_media():
    from PIL import Image, ImageDraw
    yue_local=Q/'yue-silent-study.mp4'
    movies = {'yue':yue_local if yue_local.exists() else V/'out/BOI-HK_v13_人物手風琴_畫面試片_無配音.mp4',
              'en':Q/'en-silent-study.mp4','zh-CN':Q/'zh-CN-silent-study.mp4'}
    frames = sorted(set([30,*[60+72*i+12 for i in range(6)],*[60+72*i+27 for i in range(6)],
                         *range(142,150),500,540,602]))
    media = {}
    for locale, movie in movies.items():
        info = probe(movie); streams = info['streams']
        video = next(s for s in streams if s['codec_type']=='video')
        assert video['nb_frames']=='603' and video['width']==1920 and video['height']==1080 and video['avg_frame_rate']=='30/1', info
        assert abs(float(info['format']['duration'])-20.1)<.002, info
        assert not any(s['codec_type']=='audio' for s in streams), info
        subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(movie),'-f','null','-'],check=True)
        dest = Q/f'actual-{locale}'; dest.mkdir(exist_ok=True)
        expression = '+'.join(f'eq(n\\,{f})' for f in frames)
        subprocess.run(['ffmpeg','-v','error','-i',str(movie),'-vf','select='+expression,
                        '-vsync','0','-start_number','0','-y',str(dest/'sample-%03d.png')],check=True)
        for i,f in enumerate(frames):
            (dest/f'sample-{i:03d}.png').replace(dest/f'f{f}.png')
        grid = Image.new('RGB',(1920,((len(frames)+3)//4)*300),'#182630'); draw = ImageDraw.Draw(grid)
        for i,f in enumerate(frames):
            x,y=i%4*480,i//4*300
            grid.paste(Image.open(dest/f'f{f}.png').resize((480,270)),(x,y+28))
            draw.text((x+10,y+9),f'{locale} / Actual f{f} / {f/30:.3f}s',fill='white')
        grid.save(Q/f'actual-contact-{locale}.jpg',quality=93)
        media[locale]={'path':str(movie),'sha256':sha(movie),'probe':info,'full_decode':True,
                       'audio_stream':False,'actual_sample_frames':frames}
    # One compact shared comparison: first settled lead / low-resolution lead /
    # last lead / partners for each language, decoded from actual final studies.
    show=[87,231,447,540]
    comparison=Image.new('RGB',(1920,900),'#182630');draw=ImageDraw.Draw(comparison)
    for row,locale in enumerate(LOCALES):
        for col,f in enumerate(show):
            comparison.paste(Image.open(Q/f'actual-{locale}/f{f}.png').resize((480,270)),(col*480,row*300+28))
            draw.text((col*480+10,row*300+8),f'{locale} / f{f}',fill='white')
    comparison.save(Q/'actual-contact.jpg',quality=94)
    return media


def write_report(r):
    s=r['stats']
    text=f'''# Independent people visual-study QA

Scope: three locales x603frames,20.1seconds; silent visual studies, not the finished Prompt14 long film or actual new-VO timing. No production component, data, Root or audio was edited by this reviewer.

- Browser checks: {r['checks']}, failures: {r['failure_count']}.
- All three locales cover603unique native1920x1080 browser frames.
- Maximum actual photo-row width error including5x8px gaps: {s['max_photo_width_error_px']:.6f}px.
- Maximum source-image scale including motion: {s['max_native_scale']:.9f} (limit1.6).
- All photos retain color: maximum computed grayscale {s['max_computed_grayscale']:.6f}; actual saturation spans {s['min_computed_saturation']:.6f}..{s['max_computed_saturation']:.6f}, following .55+.35*focus. Card opacity follows .65+.35*focus; effective opacity includes scheduled ancestor entrance/exit, maximum error {s['max_effective_photo_opacity_error']:.9f}.
- Maximum manual source framing-eye reference error: {s['max_eye_error_px']:.6f}px (limit1px). These source-pixel points are compositional references, not biometric identity claims.
- Minimum positive photo-to-visible-name/role/merit glyph clearance: {s['min_visible_photo_text_gap_px']:.6f}px.
- Minimum visible-merits-to-caption glyph clearance: {s['min_merits_caption_gap_px']:.6f}px.
- Minimum Range font-box clearance from photos: {s['min_font_box_photo_gap_px']:.6f}px; from caption Range: {s['min_font_box_caption_gap_px']:.6f}px.
- Maximum observed merit lines: {s['max_observed_merits_lines']}; each visible name uses the required serif family.
- Same-owner name-role and role-merits Range font boxes are checked independently of glyph ink. Both must remain disjoint for this study to pass.
- All original{r['protected_total']} protected files and the US selection remain unchanged.
- Three videos are603frames/20.1seconds/1080p30, no audio stream, complete decode successful. Actual decoded sample contact sheets accompany this report.

## Font boxes versus visible ink

There are{r['range_font_box_overlap_count']} sampled pairs whose DOM Range font-reserve boxes intersect. None intersects in the separately measured Canvas glyph-ink boxes. These are distinct measurements; this report does not call the Range-box overlap count zero or claim raster glyph segmentation. Detailed pairs are retained in verification.json.

## Limits

Width, photo crop viewport, raw scale and eye positions are actual browser layout measurements. Saturation and zero grayscale are checked from actual computed CSS filters; actual computed card opacity and effective opacity are checked including ancestor entrance/exit. These are not independent per-pixel filter analyses. Canvas text bounds use actual browser font metrics and DOM-wrapped lines. The original VO and full-film BGM were not part of these silent visual studies; no final insertion length, completed full-film integration or user visual approval is claimed.
'''
    (Q/'INDEPENDENT_VISUAL_QA.md').write_text(text)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--partial',action='store_true')
    parser.add_argument('--qa-dir',type=Path,default=Q,help='isolated study QA directory; absolute or relative to current working directory')
    args=parser.parse_args();Q=args.qa_dir.resolve()
    raise SystemExit(main(args.partial))
