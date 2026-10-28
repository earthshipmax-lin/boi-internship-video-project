from pathlib import Path
import json
V=Path(__file__).resolve().parents[1];Q=V/'qa/v20';d=json.load(open(Q/'deliverables.json'))
text='''> **2026-10-28 V20 无人物三语版**：按Prompt20删去全部人物镜及对应六句旁白/字幕，办公室／信任接大树生长。普通话73.233秒、粤语76.267秒、英文72.067秒；用户选择音乐接点A，原音量与PCM保持优先，普通话沿用已获认可的V19片尾。入口 `video/src/index-v20.tsx`、`video/qa/v20/IMPLEMENTATION.md` 和 `video/qa/v20/FINAL_QA.md`，输出 `video/out/BOI-HK_史詩形象片_v20_{普通話,粵語,英文}_無人物版.mp4`，各附20秒预览。新整片待用户观看；A接点选择不等于全片已批准。本轮按Prompt20只本地保存，不上传、不发布。旧成片和原交付ZIP保留。

'''
for p in [V/'README.md',V.parent/'CLAUDE_HANDOFF.md']:
 s=p.read_text()
 if not s.startswith('> **2026-10-28 V20'):p.write_text(text+s)
p=V/'qa/v11/CURRENT_SELECTION.json';s=json.load(open(p));s['updated']='2026-10-28';s['phase']='hk_v20_no_people_three_languages';s['evidence']='user_selected_music_join_A; complete_film_review_pending';s['next_gate']='User watches new V20 full three-language films; no new voice selection required';s['previous_video_candidate_before_v20']=s['video_candidate'];s['video_candidate']={'entry':'video/src/index-v20.tsx','status':'new_v20_complete_pending_subjective_review','qa':'video/qa/v20/FINAL_QA.md','locales':d};s['v20_authorizations']={'retainLoudness':True,'musicJoin':'A','allThreeLanguages':True,'upload':False};p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
