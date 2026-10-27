#!/usr/bin/env python3
"""Validate Stage9 route browser audits: input-routes.json output.json.

Inputs named *stills* permit sampled coverage; other names require every map
frame 864..1140 inclusive. No video or production source is changed.
"""
import hashlib
import itertools
import json
import math
import re
import sys
from pathlib import Path

NUM = r"[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?"
EXPECTED = {"深圳": (34.16, .45, 5), "紐約": (34.52, 1.05, 8), "新加坡": (35.60, .85, 5)}
ARRIVALS = {"香港": 33.38, **{n: a+d for n,(a,d,_) in EXPECTED.items()}}
NAMES = set(ARRIVALS)
TOL = .002


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def nums(d):
    return [float(v) for v in re.findall(NUM, d)]


def distance(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])


def safe(r):
    return (r['x'] >= 40-TOL and r['y'] >= 40-TOL and
            r['x']+r['width'] <= 1880+TOL and r['y']+r['height'] <= 1040+TOL and
            r['width'] > 0 and r['height'] > 0)


def overlap(a, b):
    return (min(a['x']+a['width'], b['x']+b['width'])-max(a['x'], b['x']) > TOL and
            min(a['y']+a['height'], b['y']+b['height'])-max(a['y'], b['y']) > TOL)


def main(source, output):
    video = Path(__file__).resolve().parent.parent
    component = video/'src/components/GeographicNetworkStage9.tsx'
    config = video/'src/config/routes-stage9.ts'
    world = json.loads((video/'src/assets/world-v12.json').read_text())
    xy = {n: c['xy'] for n,c in world['cities'].items()}
    raw = json.loads(source.read_text())
    rows = list(raw.values()) if isinstance(raw, dict) else raw
    errors, checks, peaks, lengths = [], 0, {}, {}
    max_vertex = max_arc = max_endpoint_error = 0
    lowest_margin = float('inf')
    actual_frames = [r['frame'] for r in rows]
    expected_frames = set(range(864,1141))
    full = set(actual_frames) == expected_frames and len(actual_frames) == 277
    partial = 'stills' in source.name.lower()

    def ck(ok, frame, rule, evidence=None):
        nonlocal checks
        checks += 1
        if not ok:
            errors.append(dict(frame=frame, rule=rule, evidence=evidence))

    ck(len(set(actual_frames)) == len(actual_frames), None, 'unique frame records')
    ck(bool(rows), None, 'nonempty route audit')
    if not partial:
        ck(full, None, 'all 277 map frames audited', sorted(expected_frames-set(actual_frames)))
    # The browser logs do not contain all unmodulated points. Inspect the exact
    # production expression as static evidence; numeric checks below separately
    # inspect final route vertices and browser-reported lengths.
    code, conf = component.read_text(), config.read_text()
    formula_checks = {
        'base_120': bool(re.search(r'baseSamples\s*:\s*120', conf)),
        't_i_over_119': 'i/(modulation.baseSamples-1)' in code,
        'normal_envelope_and_cycles': 'route.amplitude*Math.sin(Math.PI*t)*Math.sin(2*Math.PI*modulation.cycles*t)' in code,
        'cycles_2_5': bool(re.search(r'cycles\s*:\s*2\.5', conf)),
        'browser_arc_sampling': 'path.getPointAtLength(s)' in code and 'path.getTotalLength()' in code,
        'extra_subdivision': 'Math.ceil(distance(a,b)/modulation.maxVertexStep)' in code,
    }
    for rule, ok in formula_checks.items():
        ck(ok, None, 'static formula reference: '+rule)

    for row in rows:
        f, time, pan = row['frame'], row['time'], row['geographicDriftX']
        root = row['rootRect']
        ck(row['layoutValid'] is True and abs(root['width']-1920)<TOL and abs(root['height']-1080)<TOL,
           f, 'valid 1920x1080 browser layout', root)
        ck(row['localInsetCount'] == 0, f, 'no local enlargement inset')
        ck(-40-TOL <= pan <= TOL, f, 'shared geographic drift within -40..0', pan)
        labels = row['labels']
        ck({a['name'] for a in labels} == NAMES and len(labels)==4, f, 'exactly four city labels')
        for label in labels:
            name, box, peak = label['name'], label['bbox'], label['peakBBox']
            ck(safe(box), f, 'current label frame inside 40px safe region', name)
            ck(safe(peak), f, '106% peak label frame inside 40px safe region', name)
            for b in [box,peak]:
                lowest_margin = min(lowest_margin,b['x'],b['y'],1920-b['x']-b['width'],1080-b['y']-b['height'])
            ck(abs(label['start']-ARRIVALS[name])<1e-8, f, 'label starts at matching city arrival', name)
            ck(label['visible'] is (time >= ARRIVALS[name]), f, 'label visibility obeys narration-gated arrival', name)
            ck(1-TOL <= label['scale'] <= 1.06+TOL and abs(label['peakScale']-1.06)<1e-8,
               f, 'label pulse within 100..106%', name)
            ck(distance(label['origin'],[xy[name][0]+pan,xy[name][1]])<TOL,
               f, 'label origin follows common geographic drift', name)
            if name in ['香港','深圳']:
                ck(abs(label['leaderLength']-40)<TOL, f, 'HK/SZ leader length is 40px', name)
            if name not in peaks or label['scale'] > peaks[name]['scale']:
                peaks[name]=dict(frame=f,scale=label['scale'])
        for a,b in itertools.combinations(labels,2):
            if a['visible'] and b['visible']:
                ck(not overlap(a['bbox'],b['bbox']), f, 'visible city label frames do not intersect', [a['name'],b['name']])
            ck(not overlap(a['peakBBox'],b['peakBBox']), f, 'simultaneous peak label frames do not intersect', [a['name'],b['name']])

        rs=row['routes']
        ck(len(rs)==3 and {r['name'] for r in rs}==set(EXPECTED), f, 'exactly three HK-origin routes')
        for r in rs:
            name=r['name']; start,duration,amp=EXPECTED[name]
            ck(r['inset'] is False, f, 'route has no inset duplicate', name)
            ck(abs(r['start']-start)<1e-8 and abs(r['duration']-duration)<1e-8,
               f, 'route start/duration matches locked narration gate', name)
            ck(r['baseSampleCount']==120 and r['sampleCount']>=120, f, '120 formula samples retained before subdivision', name)
            ck(r['amplitude']==amp, f, 'main/subroute amplitude is 8/5', name)
            expected_offset=amp*max(abs(math.sin(math.pi*i/119)*math.sin(5*math.pi*i/119)) for i in range(120))
            ck(abs(r['maxNormalOffset']-expected_offset)<1e-8, f, '120-sample formula offset agrees with declared amplitude', name)
            base=r['baseCubicD']; mod=r['d']
            ck(len(re.findall('[Cc]',base))==1 and re.fullmatch(r'\s*M[^A-DF-Za-df-z]*C[^A-DF-Za-df-z]*',base) is not None,
               f, 'one cubic base route only', name)
            b=nums(base)
            ck(len(b)==8, f, 'base cubic has start/two controls/end', name)
            ck(re.fullmatch(r'[ML0-9eE+\.\-\s]+',mod) is not None and mod.count('M')==1,
               f, 'visible path is one continuous modulated polyline', name)
            values=nums(mod); points=list(zip(values[::2],values[1::2]))
            ck(len(values)%2==0 and len(points)==r['sampleCount'], f, 'logged vertex count equals actual path vertices', name)
            actual_step=max(distance(a,b) for a,b in zip(points,points[1:]))
            max_vertex=max(max_vertex,actual_step);max_arc=max(max_arc,r['maxArcSampleStep'])
            ck(actual_step<=5+1e-6 and r['maxSampleStep']<=5+1e-6 and r['maxArcSampleStep']<=5+1e-6,
               f, 'actual vertices and browser arc sample distance <=5px', dict(name=name,actual_step=actual_step,arc_step=r['maxArcSampleStep']))
            ck(abs(actual_step-r['maxVertexStep'])<1e-8, f, 'reported vertex maximum equals independent computation', name)
            for measured,expected,role in [(r['origin'],xy['香港'],'browser start'),(r['endpoint'],xy[name],'browser end'),
                                           (points[0],xy['香港'],'polyline start'),(points[-1],xy[name],'polyline end')]:
                error=distance(measured,expected);max_endpoint_error=max(max_endpoint_error,error)
                ck(error<TOL, f, 'local-coordinate endpoint does not drift: '+role, name)
            if len(b)==8:
                a=xy['香港']; end=xy[name]; dx=end[0]-a[0];dy=end[1]-a[1];l=math.hypot(dx,dy)
                nx,ny=-dy/l,dx/l
                if ny>0:nx,ny=-nx,-ny
                expected=[*a,a[0]+dx*.28+nx*l*.18,a[1]+dy*.28+ny*l*.18,
                          a[0]+dx*.72+nx*l*.18,a[1]+dy*.72+ny*l*.18,*end]
                ck(max(abs(x-y) for x,y in zip(b,expected))<TOL, f, 'base cubic controls match original geographic formula', name)
            lengths[name]=dict(base_length=r['baseLength'],modulated_length=r['length'],base_samples=r['baseSampleCount'],
                               subdivided_vertices=r['sampleCount'],max_vertex_step=actual_step,max_browser_arc_step=r['maxArcSampleStep'])

    for name,peak in peaks.items():
        target=ARRIVALS[name]+.12
        contains_peak_window=any(abs(r['time']-target)<=1/30+1e-8 for r in rows)
        if full or contains_peak_window:
            ck(1.05<=peak['scale']<=1.07, peak['frame'], 'actual sampled peak is 106% +/-1%', dict(name=name,**peak))
        peak['near_peak_frames_present']=contains_peak_window
    result=dict(passed=not errors,input=str(source.resolve()),input_sha256=sha(source),checks=checks,failure_count=len(errors),
                failures=errors[:100],coverage=dict(sampled_frames=len(rows),expected_map_frames=277,full_coverage=full,
                mode='stills_partial_allowed' if partial else 'all_map_frames_required',missing_frames=sorted(expected_frames-set(actual_frames))),
                static_formula_evidence=dict(checks=formula_checks,component_sha256=sha(component),config_sha256=sha(config)),
                route_metrics=lengths,actual_peaks=peaks,minimum_label_edge_clearance_px=lowest_margin,
                maxima=dict(actual_vertex_step=max_vertex,browser_arc_step=max_arc,local_endpoint_error=max_endpoint_error),
                coordinate_notes='Route origin/endpoints remain local geographic coordinates; label origins/bboxes include the common land/path/city drift.',
                limitations=['Bounding boxes are browser font element frames, not raster glyph ink.',
                             'The modulation expression is verified in source; final vertex spacing, endpoints and logged maximum normal offset are checked independently.',
                             'Static formula checks are not substituted for actual browser route length and label measurements.'])
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['passed','checks','failure_count','coverage','actual_peaks','maxima']},ensure_ascii=False))
    return 0 if not errors else 1


if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit(__doc__)
    raise SystemExit(main(Path(sys.argv[1]),Path(sys.argv[2])))
