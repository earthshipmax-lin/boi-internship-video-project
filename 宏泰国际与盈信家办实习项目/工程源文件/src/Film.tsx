import React from 'react';
import {AbsoluteFill,Sequence,Audio,staticFile} from 'remotion';
import {hk,type SceneId} from './config/hk';
import {theme,clamp01,reveal} from './theme';
import {SCENES,LogoScene} from './scenes/Scenes';
import {useMediaAssets} from './media';
import {CaptionTrack,VoiceStatus} from './components/Captions';
import './fonts';
export type SceneUnitProps={id?:SceneId;title?:string;duration?:number};
export const SceneUnit:React.FC<SceneUnitProps>=({id='S1',title,duration})=>{
 const scene=hk.scenes.find(s=>s.id===id)!; const assets=useMediaAssets();
 if(id==='S0')return <LogoScene/>;
 const C=SCENES[id];return <C scene={scene} assets={assets} title={title} duration={duration}/>;
};
export const CaptionUnit:React.FC<SceneUnitProps>=({id='S1'})=>{
 const scene=hk.scenes.find(s=>s.id===id)!; const assets=useMediaAssets();
 return <><CaptionTrack scene={scene} assets={assets}/><VoiceStatus scene={scene} assets={assets}/></>;
};
export const AudioTrack:React.FC<{bgm?:boolean}>=({bgm=true})=>{
 const assets=useMediaAssets();
 const voices=hk.scenes.filter(s=>s.vo&&assets[s.vo]);
 return <>
  {voices.map(s=>{
   const slot=s.end-s.start-hk.subtitle.leadIn-hk.subtitle.tail;
   const duration=assets[s.vo!].duration;
   if(duration>slot+.04)throw new Error(`${s.id}: extend the scene to fit natural narration; speech speed-up is disabled`);
   return <Sequence key={s.id} from={Math.round((s.start+hk.subtitle.leadIn)*hk.fps)} durationInFrames={Math.ceil(duration*hk.fps)}>
    <Audio src={staticFile(s.vo!)} playbackRate={1} volume={1}/>
   </Sequence>;
  })}
  {bgm&&assets[hk.music.file]&&<Audio src={staticFile(hk.music.file)} loop volume={f=>{
   const t=f/hk.fps;
   const voice=voices.find(s=>{
    const duration=Math.min(assets[s.vo!].duration,s.end-s.start-hk.subtitle.leadIn-hk.subtitle.tail);
    return t>=s.start+hk.subtitle.leadIn-.15&&t<s.start+hk.subtitle.leadIn+duration+.2;
   });
   const envelope=Math.min(clamp01(t/hk.music.fadeIn),clamp01((hk.duration-t)/hk.music.fadeOut));
   return (voice?hk.music.duckVolume:hk.music.volume)*envelope;
  }}/>}
 </>;
};
export const Film:React.FC<{bgm?:boolean}>=({bgm=true})=><AbsoluteFill style={{background:theme.color.paper}}>
 {hk.scenes.map(s=><Sequence key={s.id} name={s.id} from={Math.round(s.start*hk.fps)} durationInFrames={Math.round((s.end-s.start)*hk.fps)}><SceneUnit id={s.id}/></Sequence>)}
 {hk.scenes.filter(s=>s.id!=='S0').map(s=><Sequence key={`captions-${s.id}`} name={`字幕 ${s.id}`} from={Math.round(s.start*hk.fps)} durationInFrames={Math.round((s.end-s.start)*hk.fps)}><CaptionUnit id={s.id}/></Sequence>)}
 <AudioTrack bgm={bgm}/>
</AbsoluteFill>;
