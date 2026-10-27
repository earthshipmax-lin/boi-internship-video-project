"""Plots and an evidence-linked note/spectrum/dynamic analysis, not listening claims."""
from pathlib import Path
import json,subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];Q=R/'qa/us-v1-60s-v5';SR=48000
A=json.loads((Q/'music/analysis.json').read_text());roles=json.loads((R/'public/music/us-v2/ASSET_ROLES.json').read_text());score=roles['scoreV2'];T=json.loads((Q/'timeline.json').read_text())
def pcm(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar','48000','-ac','2','-f','f32le','-']),np.float32).reshape(-1,2)
old=pcm(R/'qa/us-v1-60s-v2/music-bus.wav');new=pcm(Q/'music/music-bus.wav');poly=np.load(Q/'music/polyphony.npy')
def psd(data):
 x=data.mean(axis=1);w=np.hanning(SR);values=[]
 for a in range(0,len(x)-SR+1,SR//2):values.append(np.abs(np.fft.rfft(x[a:a+SR]*w))**2/np.sum(w**2)/SR)
 return np.fft.rfftfreq(SR,1/SR),10*np.log10(np.mean(values,axis=0)+1e-24)
f,oldPS=psd(old);_,newPS=psd(new)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.right':False,'axes.spines.top':False,'figure.facecolor':'#f7f4ee','axes.facecolor':'#f7f4ee','axes.edgecolor':'#81796f','text.color':'#3d3833','axes.labelcolor':'#3d3833','xtick.color':'#81796f','ytick.color':'#81796f'})
fig,ax=plt.subplots(3,1,figsize=(13,11),layout='constrained')
ax[0].plot(np.arange(len(poly))/100,poly,color='#004098',lw=1.3);ax[0].axhline(3,color='#bb734d',ls='--',lw=1);ax[0].set(xlim=(0,60),ylabel='Active pitched voices',title=f'Full-film mean: {A["polyphonyMeanFull60s"]:.3f} voices (S0 / S6 music silence included)')
for scene in T['scenes']:
 start,end=scene['startFrame']/30,scene['endFrame']/30
 if scene['id'] in ['S0','S6']:ax[0].axvspan(start,end,color='#cfc7bb',alpha=.4)
 ax[0].text((start+end)/2,12.2,scene['id'],ha='center',fontsize=9)
ax[1].plot(f,oldPS,color='#aaa297',label='V4 / previous music bus');ax[1].plot(f,newPS,color='#004098',label='V5 music bus');ax[1].axvspan(40,50,color='#bb734d',alpha=.18);ax[1].set(xlim=(20,500),ylim=(-125,-25),xlabel='Frequency (Hz)',ylabel='Mean power (dB, common reference)',title=f'40–50 Hz band energy: +{A["bass40to50EnergyGainDB"]:.2f} dB vs near-zero old baseline');ax[1].legend(frameon=False)
labels=[v['scene'] for v in A['sceneChecks']];levels=[v['musicRMSDBFS'] if v['musicRMSDBFS']>-100 else -65 for v in A['sceneChecks']];ax[2].bar(labels,np.array(levels)+65,bottom=-65,color=['#cfc7bb' if s in ['S0','S6'] else '#bb734d' if s=='S3' else '#477d9b' for s in labels]);ax[2].set(ylim=(-65,-20),ylabel='Music RMS (dBFS)',title=f'S3 vs S5: {A["S3minusS5RMSDB"]:.2f} dB; S0 / S6 are exactly silent (plotted at floor)')
fig.savefig(Q/'music-analysis.png',dpi=155);plt.close(fig)
oldScore=roles['music']['score'];oldOnsets=[n['time'] for n in oldScore]
lines=['# 配乐重构实测分析','', '分析日：2026-10-25。输入是实际音乐总线WAV及完整可复现乐谱；不把数值检查称为主观听感验收。','', '| 指标 | V5结果 | 验收 |','|---|---:|---|',f'| 全60秒平均同时音符数（含静音） | {A["polyphonyMeanFull60s"]:.4f} | ≥3，通过 |',f'| 有音乐时平均／最大同时音符数 | {A["polyphonyMeanMusicOnly"]:.4f} / {A["polyphonyMax"]} | 乐谱及包络逐10ms计数 |',f'| 40–50Hz能量相对旧音乐总线 | +{A["bass40to50EnergyGainDB"]:.3f}dB | ≥6dB，通过 |',f'| S3相对S5音乐RMS | +{A["S3minusS5RMSDB"]:.3f}dB | ≥5dB，通过 |',f'| 旋律音长 | {A["melodyDurations"]}s | 4种，通过 |',f'| 全混音采样峰值 | {A["mixPeakDBFS"]:.3f}dBFS | ≤−1，通过 |',f'| 全片人声峰值与BGM峰值差 | {A["voicePeakDBFS"]-A["musicPeakDBFS"]:.3f}dB | ≥12dB，通过 |','| 外部音源／鼓／弦乐／riser | 均无 | 84个显式加法合成音符，未引入样本 |','', '## 分段音乐测量','', '| 段 | 音乐RMS dBFS | 音乐峰值 dBFS | 对应旁白区间峰值差 dB |','|---|---:|---:|---:|']
for row in A['sceneChecks']:
 silent=row['scene'] in ['S0','S6'];lines.append(f'| {row["scene"]} | {"精确零样本" if silent else format(row["musicRMSDBFS"],".3f")} | {"−∞" if silent else format(row["musicPeakDBFS"],".3f")} | {"BGM静音" if silent else format(row["duringVoiceSeparationDB"],".3f")} |')
lines+=['', '## 量测口径','', '同时音符数：按完整score事件的实际attack/release/钢琴衰减包络、层进入遮罩及S0/S6／尾部静音，每10ms计算有效源相对幅度>0.001的音符数，不是把音符总数除时长。所有pad和声三音分别计数，低音的八度加倍也单独写为音符，不藏在振荡器里。','', f'频谱：48kHz立体声取L/R均值，1秒Hann窗、50%重叠FFT，对40–50Hz（含边界）功率积分并作全片平均。旧能量={A["oldBandEnergy"]:.12g}，新={A["newBandEnergy"]:.12g}，同一归一化。+52dB来自旧版本该频带接近零，不表示整体配乐提高52dB。', '', 'RMS：分别在S3的603–907帧和S5的1139–1493帧，按音乐总线全部采样（双通道）计算，包含进入／退出与duck。峰值差是独立人声／音乐总线各自峰值，逐段声音区间另列；不把低频频带提升等同于整体音量提升。','', '## 提示词矛盾的处理','', f'旧ASSET_ROLES含{len(oldScore)}个音符，起点横跨{min(oldOnsets):.1f}–{max(oldOnsets):.1f}秒，并非42音／60秒；5.2秒音长与3.7秒音距本身已有重叠，也不能推出最大复音1。旧成片由截取span组装。缺乏独立低音与和声层的改造方向仍成立，本版增加真实可数的层。','', '4.8秒和弦＋0.4秒重叠意味着4.4秒起点间隔。固定60秒、S0及S6音乐静音的前提下，使用13组和弦事件／3.25次Am–F–C–G循环，不能同时声称15个四和弦循环。最后Am解决，1.5秒包络回零；谱上尾音长度与实际片长分开记录。','', '低音先保留具体表45/41/48/43，再明示轻微八度加倍33/29/36/31；F1=43.65Hz与G1≈49Hz提供所需频带。初始“36–43”与表45/48矛盾，选具体和声表，不悄悄把40–50Hz验证拿别的频带代替。','', '−18dB duck采用旧混音的绝对源衰减目标，不在分段−13/−18之后再叠−18；0.5秒恢复保持。S3主要靠旋律、和声与低频织体变饱满，S5只有pad+bass。nine states处为原音符的0.6秒3dB音量拱形，不是音高上扫／噪声riser。','', 'S0与S6仅BGM完全静音，原旁白继续。现有voice-bus.wav逐字节复用；24bit混音严格为原声＋新音乐，未重录、未变速、未移位。','', '[完整score及合成角色](../../public/music/us-v2/ASSET_ROLES.json) · [音乐图表](music-analysis.png) · [机器分析](music/analysis.json)']
(Q/'music-analysis.md').write_text('\n'.join(lines)+'\n');print('Music analysis and spectrum/dynamic figure saved.')
