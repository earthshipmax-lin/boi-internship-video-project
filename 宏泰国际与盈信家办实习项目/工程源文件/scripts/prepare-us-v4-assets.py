"""Prepare source-only office assets for Prompt17. Never edits original/HK assets."""
from pathlib import Path
import hashlib,json,csv
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[1];Q=R/'qa/us-v1-60s-v4';OUT=R/'public/stills/us-v4';OUT.mkdir(parents=True,exist_ok=True)
source=json.loads((R/'qa/v12/offices/assets/asset-manifest.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def grade(im):
    a=np.asarray(im.convert('RGB'),dtype=np.float64)/255
    lum=np.sum(a*np.array([.2126,.7152,.0722]),axis=2,keepdims=True)
    a=lum+(a-lum)*.55
    a=a*.96
    a=(a-.5)*1.02+.5
    a=np.clip(a,0,1)
    a=a*(.9+.1*np.array([61,56,51])/255)
    a=a*255+np.array([2,0,-1])
    return Image.fromarray(np.clip(np.round(a),0,255).astype(np.uint8),'RGB')
notes={
 'hk-main':'宏泰中英Logo发光墙、波纹弧形前台及花束，对应香港页右上照片。',
 'hk-upper':'Silvercord/新港中心外墙与BURBERRY店面、行人天桥，对应香港页左侧大图。',
 'hk-lower':'圆桌与白椅、黑墙电视、落地灯，匹配香港页下左休息区；旧副本已裁掉源拼图边界。',
 'sz-main':'长会议桌、落地窗与蓝色显示屏，匹配深圳页中左照片。',
 'sz-upper':'花束、窗边书桌与办公椅，匹配深圳页上左照片。',
 'sz-lower':'弧形顶灯、橙色长沙发与植物，匹配深圳页上中照片。',
 'ny-main':'宏泰Logo大理石墙、长前台与沙发，匹配美国页上左照片。',
 'ny-upper':'奖杯长柜、格栅及浅色座椅，匹配美国页上中照片。',
 'ny-lower':'橙色办公椅、转角窗与书桌，匹配美国页中左照片。'}
placements=[
 dict(id='fig01',scene='S1',asset='hk-main',figure='FIG. 01 — Hong Kong',x=1096,y=244,width=620,height=465,position=[.5,.5]),
 dict(id='fig02',scene='S3',asset='hk-lower',figure='FIG. 02 — Hong Kong',x=1180,y=172,width=596,height=196,position=[.5,.55]),
 dict(id='fig03',scene='S3',asset='sz-main',figure='FIG. 03 — Shenzhen',x=1180,y=420,width=596,height=196,position=[.5,.56]),
 dict(id='fig04',scene='S3',asset='ny-main',figure='FIG. 04 — New York',x=1180,y=668,width=596,height=196,position=[.45,.31]),
 dict(id='fig05',scene='S5',asset='ny-main',figure='FIG. 05 — Flushing, New York',x=200,y=300,width=640,height=280,position=[.45,.35]),
]
assets=[]
for city in source['cities']:
    for a in city['images']:
        p=R/'public'/a['file'];im=Image.open(p).convert('RGB');used=[v for v in placements if v['asset']==a['id']]
        record=dict(id=a['id'],city=city['english'],sourcePage=a['source_page'],sourceFile=a['source'],file=a['file'],size=list(im.size),sha256=sha(p),visualMatch=notes[a['id']],evidence='visual match to labeled source PDF office page; physical geolocation not independently verified',used=bool(used))
        if used:
            dest=OUT/(a['id']+'.png');grade(im).save(dest)
            record.update(gradedFile=str(dest.relative_to(R/'public')),gradedSha256=sha(dest))
        assets.append(record)
for p in placements:
    a=next(a for a in assets if a['id']==p['asset']);w,h=a['size'];scale=max(p['width']/w,p['height']/h)
    p.update(file=a['gradedFile'],nativeSize=a['size'],sourcePage=a['sourcePage'],scale=scale)
    assert scale<=1
manifest=dict(date='2026-10-25',sourcePDF='宏泰国际公司介紹_SC_2026年10月14日.pdf',sourcePageNumbering='physical PDF pages, 1-based',grade=dict(saturation=.55,brightness=.96,contrast=1.02,multiplyInk='#3d3833',multiplyOpacity=.10,warmRGB=[2,0,-1],pipeline='sRGB saturation Rec709; brightness; contrast around .5; multiply overlay; additive 8-bit offsets; round/clamp; no resizing'),map='Prompt17 fallback: exact 9 source state names; untraceable original map omitted',assets=assets,placements=placements)
(Q/'assets/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(R/'src/config/us-v4-photos.json').write_text(json.dumps(placements,ensure_ascii=False,indent=2)+'\n')
with (Q/'assets/scale-table.csv').open('w') as f:
    writer=csv.writer(f);writer.writerow(['figure','scene','asset','source_page','native_w','native_h','render_w','render_h','scale','no_upscale'])
    for p in placements:writer.writerow([p['id'],p['scene'],p['asset'],p['sourcePage'],*p['nativeSize'],p['width'],p['height'],p['scale'],p['scale']<=1])
rows=['# 办公室照片来源与城市归属','', '核对日：2026-10-25。逐张目视照片并对照公司PDF物理第34页（美国／Flushing）、35页（深圳）、36页（香港）。城市判定来自照片与有标签的原页匹配，未仅凭文件名前缀；不是独立现场地理定位或公司对外披露确认。八图为原生内嵌图副本，hk-lower为已保存的香港页拼图内部照片裁切。','', '| 文件 | 城市／原页 | 原生尺寸 | 本轮使用 | 目视核对依据 |','|---|---|---|---|---|']
for a in assets:
    uses=[f"{p['scene']} {p['width']}×{p['height']} / {p['scale']:.6f}×" for p in placements if p['asset']==a['id']]
    rows.append(f"| {Path(a['file']).name} | {a['city']} / p{a['sourcePage']} | {a['size'][0]}×{a['size'][1]} | {'；'.join(uses) or '已核对，未上片'} | {a['visualMatch']} |")
rows+=['', '图注14px、muted、字距.08em，直角照片，无阴影、圆角、推镜或生成补画。所有原图只读；新照片为原生尺寸PNG，统一按Prompt17第6节运算，实际显示才cover裁切。倍率以cover最大缩放计算，最大≤1.0，无额外动画缩放。','', '来源完整SHA、原生文件与显示焦点见assets/manifest.json；原香港版asset-manifest记录了hk-lower的原始裁切边界[1023,248,1819,678]。照片是公司PDF提供的实景，不能据此独立证成公司收入、当前营运状态或任何评级，图与数之间没有因果连线。','', '地图库未使用：原PDF P13地图缺少可追溯图源／授权说明，使用Prompt17第10节允许的完整九州名单，不重绘第三方地图。']
(Q/'photo-provenance.md').write_text('\n'.join(rows)+'\n')
# Evidence contact for all nine, including the previously cropped Hong Kong lounge.
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
board=Image.new('RGB',(1440,1230),'#f7f4ee');draw=ImageDraw.Draw(board)
for i,a in enumerate(assets):
    im=Image.open(R/'public'/a['file']).convert('RGB');im.thumbnail((460,345));x=i%3*480;y=i//3*410;board.paste(im,(x+(480-im.width)//2,y+20));draw.text((x+12,y+370),f"{a['id']} / {a['city']} / source p{a['sourcePage']}",font=font,fill='#3d3833')
board.save(Q/'assets/nine-photo-source-check.jpg',quality=96)
print('Prepared',len(assets),'visually matched assets;',len(placements),'placements; maximum scale',max(p['scale'] for p in placements))
