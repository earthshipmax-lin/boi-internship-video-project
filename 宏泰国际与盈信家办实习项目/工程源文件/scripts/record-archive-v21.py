from pathlib import Path
import json,time,shutil
R=Path(__file__).resolve().parents[2];V=R/'video';A=V/'qa/archive-v21-20261028'
while not (A/'cleanup-complete.json').exists():time.sleep(3)
c=json.load(open(A/'cleanup-complete.json'));r=json.load(open(A/'restore-verification.json'));g=(c['deletedMediaBytes']+c['rebuildableDependenciesBytes'])/1024**3
note=f'''# V21已获认可、GitHub归档及本地清理

2026-10-28：用户确认“可以了”，授权同步GitHub、记录过程并清理本轮本地文件。

- [V21三语成片、交付包及V20/V21工程归档](https://github.com/earthshipmax-lin/boi-internship-video-project/releases/tag/v21-final-2026-10-28)
- [项目仓库与制作复盘](https://github.com/earthshipmax-lin/boi-internship-video-project)
- [历史基础素材十卷](https://github.com/earthshipmax-lin/boi-internship-video-project/releases/tag/project-archive-2026-10-27)

本次五个附件均核对服务器SHA256/大小，并全部实际下载、SHA256一致；三部视频下载后完整解码，两份ZIP的CRC及内部文件SHA通过。增量工程内{r['archiveFilesIndividuallyVerified']}个文件逐项核验。该结论只适用于本次五个附件，不扩大为旧十卷全部重新下载验证。

已按备份清单核验原SHA后删除本轮媒体{len(c['deletedMediaFiles'])}项，{c['deletedMediaBytes']}字节，含V20/V21成片、预览、试听、QA图、ZIP与本轮恢复的旧音轨；另清理可重装的video/node_modules {c['rebuildableDependenciesBytes']}字节。二者按文件大小约{g:.2f}GiB，不把APFS实际可用空间变化与文件字节混为一谈。传输副本与本次下载校验副本另行删除。

源码、文字报告、SHA清单、原始公司资料与独立美国项目保留。恢复时将历史各卷解到项目根/video，本次增量ZIP解到项目根，再按package-lock重新安装依赖。V20/V21旧本地视频路径现已失效，请使用上述Release下载。

详细记录：video/qa/archive-v21-20261028/manifest.json、remote-verification.json、restore-verification.json、cleanup-complete.json。
'''
(R/'V21_GitHub归档与恢复说明.md').write_text(note);(A/'FINAL_ARCHIVE_RECORD.md').write_text(note)
for p in [V/'README.md',R/'CLAUDE_HANDOFF.md']:
 p.write_text('> **2026-10-28 V21已认可并归档清理**：用户授权同步及清理已执行；V20/V21本地媒体已移除。下载/恢复见项目根V21_GitHub归档与恢复说明.md，远端Release v21-final-2026-10-28。五附件均实下载SHA验证，三片解码与ZIP逐项校验通过。源码/记录保留。\n\n'+p.read_text())
p=V/'qa/v11/CURRENT_SELECTION.json';s=json.load(open(p));s['phase']='v21_user_accepted_archived_local_media_removed';s['evidence']='user_accepted; five_remote_assets_fully_downloaded_and_verified; local_cleanup_complete';s['next_gate']='No outstanding production task; restore assets before any future revision';s['archive_v21']={'url':c['release'],'localMediaRemoved':True,'record':'video/qa/archive-v21-20261028/FINAL_ARCHIVE_RECORD.md'};p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
P=R/'实习经历公开作品/宏泰国际与盈信家办实习项目/项目资料/V21归档验证与清理';P.mkdir(exist_ok=True)
for n in ['FINAL_ARCHIVE_RECORD.md','remote-verification.json','restore-verification.json','cleanup-complete.json','manifest.json','assets.json']:shutil.copyfile(A/n,P/n)
k=Path('/Users/linwenbin/Desktop/codex工作流/ex-wife/projects/boi-logo-reveal/STATUS.md');s=k.read_text();s=s.replace('# 当前进度\n\n',f'# 当前进度\n\n2026-10-28最新：用户确认V21并要求同步GitHub、记录过程、删除本轮本地媒体。公开仓库earthshipmax-lin/boi-internship-video-project已更新最终三语成片及V20/V21复盘；Release v21-final-2026-10-28含三片/交付ZIP/增量工程ZIP五附件，服务端SHA/大小匹配且全部实际下载SHA核验，三片解码、两ZIP CRC/内部SHA和增量{r["archiveFilesIndividuallyVerified"]}项通过。按校验清单删除{len(c["deletedMediaFiles"])}项媒体/{c["deletedMediaBytes"]}字节、可重装依赖{c["rebuildableDependenciesBytes"]}字节，按文件大小合计约{g:.2f}GiB；临时传输/校验副本也清理。源码/文字记录、原公司资料和独立美国项目保留。原本地V20/V21视频链接失效，改从Release下载。唯一完整证据在工作区video/qa/archive-v21-20261028/，根V21_GitHub归档与恢复说明.md为入口。本次五附件全恢复核验不扩大为旧十卷全恢复；当前授权覆盖上一轮不上傳要求。新整片已由用户认可，不推断公司另行审批。阶段Git与远端SHA另核验。\n\n## 前阶段：V21本地交付\n\n',1);k.write_text(s)
print('RECORD SAVED',round(g,2),'GiB')
