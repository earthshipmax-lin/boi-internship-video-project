from pathlib import Path
import json,shutil,hashlib
V=Path(__file__).resolve().parents[1];R=V.parent;Q=V/'qa/v16';ver=json.loads((Q/'verification.json').read_text());assert ver['full']['completeDecode'] and ver['preview']['completeDecode']
for name in ['full','preview']:assert hashlib.sha256((V/ver[name]['file']).read_bytes()).hexdigest()==ver[name]['sha256']
B=Q/'before-docs';B.mkdir(exist_ok=True)
for rel in ['README.md','../CLAUDE_HANDOFF.md','qa/v11/CURRENT_SELECTION.json']:
 src=V/rel;dst=B/rel.replace('../','root/');dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists():shutil.copy2(src,dst)
entry='''> **当前普通话：V16递进拖音版（2026-10-27），已完成，待用户听感。** 用户明确否定V15普通话片尾，此版用同一已批准男声、真实分段Happy情绪标记重新生成，保留“图”自然发音，细修“山／泰／际”局部拖音并让力度递增；片尾字幕随新声音调整。98.733333秒／2962帧；89.833333秒前V15普通话母带PCM逐样本保留。画面复用V15，粤语／英文仍以V15为当前候选，没有生成所谓V16粤英。
>
> 当前入口src/index-v16.tsx、timeline-v16-cn.json、BOI-HK-Epic-v16-CN；qa/v16/FINAL_QA.md、IMPLEMENTATION.md及verification.json。V15普通话末段不代表用户认可；其他画面未被这次反馈否定。新V16的激昂／自然感仍待用户听感，不能只凭技术通过宣称满意。

'''
links=f"[普通话V16完整版]({ver['full']['file']}) · [V16片尾预览]({ver['preview']['file']}) · [粤语V15完整版](out/BOI-HK_史詩形象片_v15_粵語_細節與聲音精修版.mp4) · [英文V15完整版](out/BOI-HK_史詩形象片_v15_英文_細節與聲音精修版.mp4) · [技术核对](qa/v16/FINAL_QA.md)。\n\n"
p=V/'README.md';s=p.read_text();p.write_text(entry+links+s[s.index('# 美国60秒'):])
p=R/'CLAUDE_HANDOFF.md';s=p.read_text();p.write_text(entry+'先读video/qa/v16/IMPLEMENTATION.md；r01字音有疑点未采用，r02是正式声源，原WAV与局部处理干声分开保存。真正的情绪标记通过选中文字后点击Emotion添加，不是按钮不可用。当前普通话只替换尾段，英文／粤语继续V15。\n\n'+s[s.index('> **最新入口：Prompt18美国'):])
p=V/'qa/v11/CURRENT_SELECTION.json';x=json.loads(p.read_text());x['prior_v15_candidate']=x['video_candidate'];current=x['video_candidate'];current['locales']['cn']={'path':'video/'+ver['full']['file'],'seconds':ver['full']['seconds'],'frames':ver['full']['frames'],'composition':'BOI-HK-Epic-v16-CN','entry':'video/src/index-v16.tsx','qa':'video/qa/v16/verification.json'};current['preview']='video/'+ver['preview']['file'];x.update(updated='2026-10-27',phase='hk_v16_mandarin_ending_complete_pending_user_emotion_review',next_gate='User listens to V16 Mandarin ending; Yue/EN remain V15.',voice_status='V15 Mandarin ending rejected. V16 same approved clone with real Happy spans, speed0.88/pitch+1, r02 selected, local vowel sustain and gentle crescendo.');x['v16']={'scope':'Mandarin ending only','protectedUnchanged':ver['protectedFilesUnchanged'],'bodyPCMUnchangedUntilSeconds':ver['bodyPCMUnchangedUntilSeconds'],'review':'User emotional acceptance pending'};p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
s='# V16 普通话片尾技术核对\n\n2026-10-27。用户明确否定V15普通话片尾；本版为重新生成及细修后的候选，情绪听感待用户。\n\n'
for k in ['full','preview']:
 a=ver[k];s+=f"- {k}：[影片](../../{a['file']})；{a['seconds']:.6f}秒／{a['frames']}帧；{a['integratedLUFS']:.2f}LUFS／{a['truePeakDBTP']:.2f}dBTP；母带相关{a['audioCorrelationToMaster']:.9f}；完整解码通过。\n"
s+=f"\n均1080p30／H264／AAC48k立体声，有声音轨，无数字削波。{ver['layoutSamples']}个原生排版抽样无文字越界；30句语音活动在字幕窗内，窗口无交叠。89.833333秒之前原V15普通话母带PCM逐采样完全相同；编码AAC经重编不能称字节相同。{ver['protectedFilesUnchanged']}个旧保护文件SHA保持，粤／英V15与美国系列不变。TypeScript通过。\n\n"
s+='声音采用已批准克隆；真实Happy情绪标记、原生speed0.88／pitch+1，三处元音WSOLA保音高延展共0.434938秒，选用干声7.220354秒，原始r02干声6.785417秒另存。声音力度轻递增，末段加入原A配乐后局部限峰，字幕按实际波形重校。r01仅备份，没入片。两次生成各55点，共110；最后观测6549点。\n\n原始r02的红／宏同音替字如实记录；最新选用处理干声独立ASR全文逐字识别正确，已用SHA确认是最终同一文件。ASR不等于完整人工听审。声线／拖音／逐渐激昂的主观效果由用户试听评价；本轮没有再次请求已批准声线的试听许可。资料来源、公司使用批准边界不变。\n\n证据：audio-implementation.json、cn-ending-alignment.json、selected-voice-asr.json、minimax-r02-proof.png、verification.json、IMPLEMENTATION.md。旧V15尾音“情绪按钮不可用”的解释已由本轮UI验证纠正；当时是未先选中台词。\n'
(Q/'FINAL_QA.md').write_text(s)
print('V16 local delivery docs saved.')
