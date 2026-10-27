import React from 'react';
import {AbsoluteFill,Freeze,useCurrentFrame,useVideoConfig} from 'remotion';
import {BrandLockup,CANOPY_ANCHOR} from './components/BrandLockup';
import {SceneBase,PressText} from './components/Motion';
import {CaptionUnit} from './Film';
import {hk} from './config/hk';
import timing from './config/logo-hk-v7.json';
import {theme,progress,reveal} from './theme';
import './fonts';

// Both bookends share the approved geometry, per-leaf transforms, easing,
// centre-out wordmark and the same accelerated clock. No glyph is redrawn.
export const BookendBrandV7:React.FC<{seconds:number;prefix:string}>=({seconds,prefix})=>
 <BrandLockup seconds={seconds*timing.logoRate} prefix={prefix} chineseOnly={false}/>;

export const LogoIntroV7:React.FC=()=>{
 const t=useCurrentFrame()/useVideoConfig().fps;
 const po=progress(t,timing.introExitStart,timing.introExitSeconds);
 // Only the existing ring exit clock is compressed; the growth clock above
 // is also reused in the outro, which has no exit.
 const exitClock=hk.logoTimeline.outStart+Math.max(0,t-timing.introExitStart)*
  (hk.logoTimeline.outDur/timing.introExitSeconds);
 return <AbsoluteFill style={{background:theme.color.paper}}>
  <AbsoluteFill style={{opacity:1-po}}><BookendBrandV7 seconds={t} prefix="v7-intro"/></AbsoluteFill>
  {t>=timing.introExitStart&&<svg width={1920} height={1080} style={{position:'absolute'}}>{Array.from({length:6},(_,i)=>{
   const p=reveal(exitClock,hk.logoTimeline.outStart+i*.12,1.8-i*.12);
   return <circle key={i} cx={CANOPY_ANCHOR.x} cy={CANOPY_ANCHOR.y} r={CANOPY_ANCHOR.radius+p*(2200+i*90)} fill="none" stroke={theme.color.terracotta} strokeWidth={1.5} opacity={(1-p)*.7}/>;
  })}</svg>}
 </AbsoluteFill>;
};

// Read the existing v6 map for the incoming rings, welcome headline and
// subtitles. Their clock is unchanged; only the logo receives a new clock.
const outroSourceFrame=(frame:number)=>{
 let cursor=0;
 for(const segment of timing.outroTiming.segments){
  if(frame<cursor+segment.outputFrames){
   return segment.sourceFrom-1968+(frame-cursor)*segment.rate;
  }
  cursor+=segment.outputFrames;
 }
 return 2191-1968;
};

const OutroLayoutV7:React.FC<{logoSeconds:number}>=({logoSeconds})=>{
 const t=useCurrentFrame()/useVideoConfig().fps,p=reveal(t,0,.5);
 const scene=hk.scenes.find(s=>s.id==='S7')!;
 return <SceneBase t={t} duration={scene.end-scene.start} fadeOut={false}>
  <svg width={1920} height={1080} style={{position:'absolute'}}>{[0,1,2,3].map(i=><circle key={i} cx={CANOPY_ANCHOR.x} cy={CANOPY_ANCHOR.y} r={CANOPY_ANCHOR.radius+(1-p)*(550+i*190)} stroke={theme.color.terracotta} strokeWidth={1.5} fill="none" opacity={(1-p)*.65}/>)}</svg>
  <AbsoluteFill style={{opacity:p,transform:'translateY(-104px) scale(.82)',transformOrigin:'center'}}><BookendBrandV7 seconds={logoSeconds} prefix="v7-outro"/></AbsoluteFill>
  <div style={{position:'absolute',top:696,left:144,right:144,textAlign:'center'}}><PressText text={scene.title[0]} t={t} delay={.3} align="center" size={theme.type.heading}/></div>
 </SceneBase>;
};

export const LogoOutroV7:React.FC=()=>{
 const f=useCurrentFrame(),fps=useVideoConfig().fps;
 return <AbsoluteFill style={{background:theme.color.paper}}>
  <Freeze frame={outroSourceFrame(f)}>
   <OutroLayoutV7 logoSeconds={f/fps}/>
   <CaptionUnit id="S7"/>
  </Freeze>
 </AbsoluteFill>;
};
