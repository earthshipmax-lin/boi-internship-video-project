from pathlib import Path
import json,shutil
V=Path(__file__).resolve().parents[1];Q=V/'qa/v13/redesign';R=V.parent
verify=json.loads((Q/'verification.json').read_text());assert len(verify['results'])==3 and not verify['layoutFailures']
backup=Q/'before-delivery-docs'
files=['README.md','../CLAUDE_HANDOFF.md','qa/v11/CURRENT_SELECTION.json','qa/v13/people/PREPARATION_STATUS.md','qa/v13/people/PHASE_DELIVERY.md','qa/v13/people/REVIEW_GATE.json','qa/v13/people/voice-production-r01/progress.json','src/config/people-v13.ts','qa/v13/full/final-r01/PRODUCTION_STATUS.md']
for rel in files:
 p=V/rel;target=backup/rel.replace('../','root/');target.parent.mkdir(parents=True,exist_ok=True)
 if not target.exists():shutil.copy2(p,target)
entry='''> **当前香港交付（2026-10-26）：Prompt14三语加长片已补齐，Prompt15五镜重设计版已完成。** 新版每片114.20秒／3426帧／1080p30，蓝背景10处共同句间缩短合计2.33秒，人声保留段逐采样一致、无变速。25标志双轨、完整两幅对联与四奖杯、精确地图单Q航线、放大平台文字、两行根深标题已接入三语。人物保留淡彩及暖灰留白≤1.6倍，A音乐继续使用。
>
> 复刻男声及三语样音均已获用户批准；全部63条新录音落盘（含2条替换，61条选用），加原5条共66条新增配音用于加长制作。英文佣金与普通话保费r02已选择。三片完整解码、168原生抽样帧布局／地图／声轨验证通过，476旧保护项及3份Prompt14加长成片保持。当前仍是待用户观看的内部审片，不代表公司批准。
>
> 具体几何适配和未达数值项见 IMPLEMENTATION.md：根深优先保持128px及树高560px，墨迹面积比并非稿内1:1.2；英文按700px宽适配为84px。旧版全部留存，不上载、不发布。

'''
links='''[粤语重设计版](out/BOI-HK_史詩形象片_v13_粵語_重設計版.mp4) · [英文重设计版](out/BOI-HK_史詩形象片_v13_英文_重設計版.mp4) · [普通话／简中重设计版](out/BOI-HK_史詩形象片_v13_簡中_重設計版.mp4) · [QA](qa/v13/redesign/FINAL_QA.md) · [适配说明](qa/v13/redesign/IMPLEMENTATION.md)。
'''
p=V/'README.md';s=p.read_text();p.write_text(entry+links+'\n\n'+s[s.index('# 美国60秒'):])
p=R/'CLAUDE_HANDOFF.md';s=p.read_text();p.write_text(entry+'香港当前入口：video/qa/v13/redesign/FINAL_QA.md、IMPLEMENTATION.md、src/config/timeline-v13-redesign.json。重渲染：node scripts/render-redesign-v13.mjs --render-only（拒绝覆写）；独立src/index-v13-redesign.tsx。旧Prompt14用原入口，不混用timeline。\n\n'+s[s.index('> **最新入口：Prompt18美国'):])
p=V/'qa/v11/CURRENT_SELECTION.json';x=json.loads(p.read_text());x['prior_stage9_candidate']=x['video_candidate'];x.update({'phase':'hk_v13_prompt15_complete_pending_user_review','evidence':'approved_scope_voice; technical_checks_complete; film_not_user_approved','voice_status':'Complete:63 downloads including2 replacements;61 selected +5 original clips.','next_gate':'User watches latest three-language films; no production blocker.','video_candidate':{'path':'video/'+verify['results']['yue']['file'],'composition':'BOI-HK-Epic-v13','entry':'video/src/index-v13-redesign.tsx','duration_seconds':114.2,'status':'completed_internal_review_not_user_approved','sha256':verify['results']['yue']['sha256'],'qa':'video/qa/v13/redesign/verification.json','locales':{l:'video/'+r['file'] for l,r in verify['results'].items()}},'prompt15':{'blueQuietCutFrames':70,'blueQuietCutCount':10,'timeline':'video/src/config/timeline-v13-redesign.json','fiveSceneQA':'video/qa/v13/redesign/geometry-voice-check.json','oldVersionsPreserved':True}})
x['prompt14_preparation']['status']='completed_superseded_by_prompt15_delivery';p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
status='''# 香港三语影片已完成，当前为Prompt15重设计版

2026-10-26。先前“等待复刻试听／网络恢复／配音未完成”的状态已被覆盖。用户批准复刻后，63条新生成音频全部保存，包含两条数字替换；61条选用，另5条原账户样音参与生产。无剩余配音任务。最后余额记录8165；不是实时余额查询。

Prompt14三语加长成片已完成并保留，每片3496帧／116.533333秒。Prompt15新版每片3426帧／114.20秒，用户最新要求压缩蓝段句间70帧。详见 [当前QA](../redesign/FINAL_QA.md)、[实现取舍](../redesign/IMPLEMENTATION.md)。三份当前视频的入口为video/README.md。

人物仍淡彩、暖灰留白、原图最大1.6倍。新旧声音、A音乐与B/C分类备份保留。下一步用户看／听新版再反馈；不重复请求已取得的样音、复刻、暖灰、时长批准。当前没有网络或额度阻塞。
'''
for name in ['PREPARATION_STATUS.md','PHASE_DELIVERY.md']:(V/'qa/v13/people'/name).write_text(status)
p=V/'qa/v13/people/REVIEW_GATE.json';x=json.loads(p.read_text());x.update({'scope':'HK Prompt14 voice gate resolved; Prompt15 film delivery pending subjective review','status':'voice_approved_full_films_delivered_pending_user_review','generation_state':'complete','new_TTS_generated':68,'selectedNewTTSClips':66,'next_after_approval':'All production delivered; await optional user feedback.','film_approved':False});p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
p=V/'qa/v13/people/voice-production-r01/progress.json';x=json.loads(p.read_text());x.update({'status':'complete_three_language_prompt15_films_delivered','remaining':0,'deliverables':{l:r['file'] for l,r in verify['results'].items()},'durationSeconds':114.2});p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
p=V/'src/config/people-v13.ts';s=p.read_text().replace('/** Prompt14 preparation. No final timing is claimed before approved VO exists. */','/** Production complete. Measured timelines are authoritative. */').replace("status:'original_samples_approved_saved_clone_pending_audition'","status:'complete_prompt15_pending_user_film_review'").replace('finalExtraFrames:null','finalExtraFrames:911').replace('finalTotalFrames:null','finalTotalFrames:3426').replace('User approved warm-gray contain; actual audio durations and final insertion length remain pending.','User approved warm-gray contain; measured people insertion911frames; Prompt15 total3426frames.');p.write_text(s)
(V/'qa/v13/full/final-r01/PRODUCTION_STATUS.md').write_text('# Prompt14三语加长版完成\n\n2026-10-26：配音、统一时间轴、三语混音与三份加长成片完成，3496帧／116.533333秒。verification.json记录完整解码与476旧保护项。后续Prompt15当前候选见../../redesign/FINAL_QA.md；本目录成片保留作为前版。\n')
print('Updated delivery docs; original docs backed up.')
