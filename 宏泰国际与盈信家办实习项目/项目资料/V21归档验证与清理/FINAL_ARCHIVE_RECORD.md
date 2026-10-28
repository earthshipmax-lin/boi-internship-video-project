# V21已获认可、GitHub归档及本地清理

2026-10-28：用户确认“可以了”，授权同步GitHub、记录过程并清理本轮本地文件。

- [V21三语成片、交付包及V20/V21工程归档](https://github.com/earthshipmax-lin/boi-internship-video-project/releases/tag/v21-final-2026-10-28)
- [项目仓库与制作复盘](https://github.com/earthshipmax-lin/boi-internship-video-project)
- [历史基础素材十卷](https://github.com/earthshipmax-lin/boi-internship-video-project/releases/tag/project-archive-2026-10-27)

本次五个附件均核对服务器SHA256/大小，并全部实际下载、SHA256一致；三部视频下载后完整解码，两份ZIP的CRC及内部文件SHA通过。增量工程内212个文件逐项核验。该结论只适用于本次五个附件，不扩大为旧十卷全部重新下载验证。

已按备份清单核验原SHA后删除本轮媒体138项，974345286字节，含V20/V21成片、预览、试听、QA图、ZIP与本轮恢复的旧音轨；另清理可重装的video/node_modules 1118232380字节。二者按文件大小约1.95GiB，不把APFS实际可用空间变化与文件字节混为一谈。传输副本与本次下载校验副本另行删除。

源码、文字报告、SHA清单、原始公司资料与独立美国项目保留。恢复时将历史各卷解到项目根/video，本次增量ZIP解到项目根，再按package-lock重新安装依赖。V20/V21旧本地视频路径现已失效，请使用上述Release下载。

详细记录：video/qa/archive-v21-20261028/manifest.json、remote-verification.json、restore-verification.json、cleanup-complete.json。

公开仓库的本地工作副本已使用Git sparse-checkout移除三部视频；远端视频保留，源码与文字记录继续保存在本地。
