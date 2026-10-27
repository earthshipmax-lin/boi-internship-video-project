import React from 'react';
import {AbsoluteFill,Freeze,useCurrentFrame,useVideoConfig} from 'remotion';
import {CANOPY_ANCHOR} from './components/BrandLockup';
import {OfficialBrandV10} from './components/OfficialBrandV10';
import {SceneBase,PressText} from './components/Motion';
import {CaptionUnit} from './Film';
import {hk} from './config/hk';
import timing from './config/logo-hk-v7.json';
import {theme,progress,reveal} from './theme';
import './fonts';

// Replace only the brand artwork with the supplied original SVG. Keep the
// existing growth clock, transition, welcome layout and caption mapping.
export const BookendBrandV10:React.FC<{seconds:number;prefix:string}>=({seconds,prefix})=>
 <OfficialBrandV10 seconds={seconds*timing.logoRate} prefix={prefix}/>;

export const LogoIntroV10:React.FC=()=>{
 const t=useCurrentFrame()/useVideoConfig().fps;
 const po=progress(t,timing.introExitStart,timing.introExitSeconds);
 // Only the existing ring exit clock is compressed; the growth clock above
 // is also reused in the outro, which has no exit.
 const exitClock=hk.logoTimeline.outStart+Math.max(0,t-timing.introExitStart)*
  (hk.logoTimeline.outDur/timing.introExitSeconds);
 return <AbsoluteFill style={{background:theme.color.paper}}>
  <AbsoluteFill style={{opacity:1-po}}><BookendBrandV10 seconds={t} prefix="v10-intro"/></AbsoluteFill>
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

const OutroLayoutV10:React.FC<{logoSeconds:number}>=({logoSeconds})=>{
 const t=useCurrentFrame()/useVideoConfig().fps,p=reveal(t,0,.5);
 const scene=hk.scenes.find(s=>s.id==='S7')!;
 return <SceneBase t={t} duration={scene.end-scene.start} fadeOut={false}>
  <svg width={1920} height={1080} style={{position:'absolute'}}>{[0,1,2,3].map(i=><circle key={i} cx={CANOPY_ANCHOR.x} cy={CANOPY_ANCHOR.y} r={CANOPY_ANCHOR.radius+(1-p)*(550+i*190)} stroke={theme.color.terracotta} strokeWidth={1.5} fill="none" opacity={(1-p)*.65}/>)}</svg>
  <AbsoluteFill style={{opacity:p,transform:'translateY(-104px) scale(.82)',transformOrigin:'center'}}><BookendBrandV10 seconds={logoSeconds} prefix="v10-outro"/></AbsoluteFill>
  <div style={{position:'absolute',top:696,left:144,right:144,textAlign:'center'}}><PressText text={scene.title[0]} t={t} delay={.3} align="center" size={theme.type.heading}/></div>
 </SceneBase>;
};

export const LogoOutroV10:React.FC=()=>{
 const f=useCurrentFrame(),fps=useVideoConfig().fps;
 return <AbsoluteFill style={{background:theme.color.paper}}>
  <Freeze frame={outroSourceFrame(f)}>
   <OutroLayoutV10 logoSeconds={f/fps}/>
   <CaptionUnit id="S7"/>
  </Freeze>
 </AbsoluteFill>;
};
