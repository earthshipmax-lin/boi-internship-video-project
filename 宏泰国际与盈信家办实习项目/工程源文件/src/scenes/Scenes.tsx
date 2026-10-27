import React from 'react';
import {AbsoluteFill,Loop,OffthreadVideo,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {hk,type SceneSpec} from '../config/hk';
import {theme,reveal,clamp01,progress} from '../theme';
import type {MediaAssets} from '../media';
import {BrandLockup,CANOPY_ANCHOR} from '../components/BrandLockup';
import {SceneBase,PressText,FineRing,ringEase,StrokePath} from '../components/Motion';
import {cueTimings} from '../components/Captions';
export type SceneProps={scene:SceneSpec;assets:MediaAssets;title?:string;duration?:number;color?:string};
const useTime=()=>useCurrentFrame()/useVideoConfig().fps;
export const LogoScene:React.FC<{transition?:boolean;still?:boolean;chineseOnly?:boolean}>=({transition=true,still=false,chineseOnly=hk.chineseOnly})=>{
 const t=useTime(),now=still?12:t;
 const po=transition?progress(t,hk.logoTimeline.outStart,hk.logoTimeline.outDur):0;
 return <AbsoluteFill style={{background:theme.color.paper}}>
  <AbsoluteFill style={{opacity:1-po}}><BrandLockup seconds={now} chineseOnly={chineseOnly}/></AbsoluteFill>
  {transition&&po>0&&<svg width={1920} height={1080} style={{position:'absolute'}}>{Array.from({length:6},(_,i)=>{
   const p=reveal(t,hk.logoTimeline.outStart+i*.12,1.8-i*.12);
   return <circle key={i} cx={CANOPY_ANCHOR.x} cy={CANOPY_ANCHOR.y} r={CANOPY_ANCHOR.radius+p*(2200+i*90)} fill="none" stroke={theme.color.terracotta} strokeWidth={1.5} opacity={(1-p)*.7}/>;
  })}</svg>}
 </AbsoluteFill>;
};
export const WhyNow:React.FC<SceneProps>=({scene,assets,title,duration})=>{
 const t=useTime();const footage=scene.footage&&assets[scene.footage];
 return <SceneBase background={theme.color.warmGray} t={t} duration={duration??scene.end-scene.start}>
  {footage&&<><Loop durationInFrames={Math.max(1,Math.round(footage.duration*hk.fps))}><OffthreadVideo src={staticFile(scene.footage!)} muted style={{position:'absolute',width:'100%',height:'100%',objectFit:'cover'}}/></Loop><AbsoluteFill style={{background:theme.color.warmGray,opacity:.78}}/></>}
  {!footage&&<div style={{position:'absolute',left:144,top:104,right:300,fontSize:28,lineHeight:1.5,color:theme.color.muted}}>{hk.labels.footagePrefix}{scene.placeholder}</div>}
  <div style={{position:'absolute',left:144,top:300}}><PressText text={title??scene.title[0]} t={t} size={theme.type.display*1.05} accent/>
   <div style={{height:40}}/><PressText text={scene.title[1]} t={t} delay={.25} size={theme.type.title}/>
   <div style={{marginTop:40,fontSize:28,color:theme.color.muted,opacity:reveal(t,.7,.4)}}>{scene.review}</div>
  </div>
 </SceneBase>;
};
export const TrustPerson:React.FC<SceneProps>=({scene,assets,title,duration})=>{
 const t=useTime();const p=reveal(t,.45,1.5);const footprint=scene.footage&&assets[scene.footage];
 return <SceneBase t={t} duration={duration??scene.end-scene.start}>
  {footprint?<><Loop durationInFrames={Math.max(1,Math.round(footprint.duration*hk.fps))}><OffthreadVideo muted src={staticFile(scene.footage!)} style={{position:'absolute',width:'100%',height:'100%',objectFit:'cover'}}/></Loop><AbsoluteFill style={{background:theme.color.paper,opacity:.82}}/></>:<svg width={1920} height={1080} style={{position:'absolute'}}>
   <circle cx={520} cy={380} r={20} fill={theme.color.ink} opacity={reveal(t,.05,.5)}/><circle cx={1400} cy={380} r={20} fill={theme.color.terracotta} opacity={reveal(t,.2,.5)}/>
   <path d="M550 380 H1370" pathLength={1} stroke={theme.color.terracotta} strokeWidth={2} strokeDasharray="1" strokeDashoffset={1-p} fill="none"/>
  </svg>}
  <div style={{position:'absolute',left:144,right:144,top:500}}><PressText text={title??scene.title[0]} t={t} delay={1.3} size={theme.type.title*1.333} align="center"/></div>
 </SceneBase>;
};
export const TreeRings:React.FC<SceneProps>=({scene,title,duration})=>{
 const t=useTime();
 return <SceneBase t={t} duration={duration??scene.end-scene.start}>
  <svg width={1920} height={1080} style={{position:'absolute'}}>{Array.from({length:7},(_,i)=><FineRing key={i} cx={1560} cy={510} r={96+i*96} p={ringEase((t-.4-i*.32)/1.4)} opacity={.7-i*.055} width={1.5}/>)}</svg>
  <div style={{position:'absolute',left:144,top:300}}><PressText text={title??scene.title[0]} t={t} size={theme.type.title*1.333}/><div style={{height:40}}/><PressText text={scene.title[1]} t={t} delay={.4} size={theme.type.title}/></div>
 </SceneBase>;
};
const ICONS=[['M-64 -60 L0 -88 L64 -60 V4 C64 55 25 82 0 96 C-25 82 -64 55 -64 4 Z','M-29 -2 L-5 23 L34 -28'],['M-45 -80 V80','M45 -80 V80','M-45 0 H45'],['M-80 -64 H80 V64 H-80 Z','M-80 -24 H80','M-40 8 H-4 M-40 34 H42']];
export const Platform:React.FC<SceneProps>=({scene,assets,title,duration})=>{
 const t=useTime();const cues=cueTimings(scene,assets);const starts=assets[scene.vo??'']?[cues[1]?.start??1,cues[2]?.start??3,cues[3]?.start??5]:scene.cueOffsets!;return <SceneBase t={t} duration={duration??scene.end-scene.start}>
  <div style={{position:'absolute',left:144,right:144,top:268,display:'flex',justifyContent:'space-between'}}>{scene.title.map((word,i)=>{
   const p=reveal(t,starts[i]??i*2,.5);
   return <div key={i} style={{width:440,textAlign:'center'}}>
    <svg width={440} height={220}><g transform="translate(220 110)">{ICONS[i].map((d,j)=><StrokePath key={j} d={d} p={p} width={2}/>)}</g></svg>
    <div style={{marginTop:56}}><PressText text={i===0&&title?title:word} t={t} delay={(starts[i]??i*2)+.15} size={theme.type.title} align="center"/></div>
   </div>;
  })}</div>
 </SceneBase>;
};
// Original, simplified Hong Kong skyline linework. No third-party photos or people.
const SKYLINE='M144 736 H218 V651 H254 V600 H272 V651 H304 V736 H344 V583 H392 V546 H406 V583 H446 V736 H500 V614 H552 V736 H600 V520 H618 V487 H636 V520 H654 V736 H698 V608 H750 V736 H804 V584 L852 405 L900 584 V736 H956 V638 H1004 V736 H1060 V562 H1095 V484 H1128 V562 H1164 V736 H1220 V602 H1276 V736 H1332 V616 H1378 V514 H1410 V616 H1456 V736 H1512 V654 H1584 V736 H1632 V628 H1680 V736 H1776';
export const HongKong:React.FC<SceneProps>=({scene,title,duration})=>{
 const t=useTime();const p=reveal(t,.1,.5);
 return <SceneBase t={t} duration={duration??scene.end-scene.start}>
  <div style={{position:'absolute',left:144,right:144,top:160}}><PressText text={title??scene.title[0]} t={t} size={theme.type.title*1.333} align="center"/></div>
  <svg width={1920} height={1080} style={{position:'absolute'}}>
   <StrokePath d={SKYLINE} p={p} color={theme.color.ink} width={2}/>
   <StrokePath d="M960 742 C890 796 720 796 552 796 H144" p={reveal(t,.4,.5)} width={2}/>
   <StrokePath d="M960 742 C1030 796 1200 796 1368 796 H1776" p={reveal(t,.4,.5)} width={2}/>
  </svg>
 </SceneBase>;
};
export const FirstYear:React.FC<SceneProps>=({scene,assets,title,duration})=>{
 const t=useTime();const cues=cueTimings(scene,assets);const starts=assets[scene.vo??'']?[cues[0]?.start??.25,cues[2]?.start??3,cues[4]?.start??6]:scene.cueOffsets!;
 return <SceneBase t={t} duration={duration??scene.end-scene.start}>
  <svg width={1920} height={1080} style={{position:'absolute'}}>{[0,1,2,3].map((i)=>{
   const start=i<2?starts[i]:starts[2]+(i===3?.45:0);
   return <FineRing key={i} cx={600} cy={490} r={96+i*64} p={ringEase((t-start)/.5)} color={theme.color.terracotta} width={i===3?2.5:1.5}/>;
  })}</svg>
  <div style={{position:'absolute',left:1000,top:238,width:800}}>{scene.title.map((word,i)=>{
   const p=reveal(t,starts[i],.5);
   return <div key={i} style={{display:'flex',alignItems:'baseline',gap:32,marginBottom:64,opacity:p,transform:`translateY(${(1-p)*16}px)`}}>
    <div style={{fontFamily:theme.font.serif,fontSize:theme.type.heading*.75,color:theme.color.terracotta,minWidth:240}}>{hk.labels.quarter[i]}</div>
    <div style={{fontFamily:theme.font.serif,fontWeight:600,fontSize:theme.type.heading,whiteSpace:'nowrap'}}>{i===0&&title?title:word}</div>
   </div>;
  })}</div>
 </SceneBase>;
};
export const Welcome:React.FC<SceneProps>=({scene,title,duration})=>{
 const t=useTime(),p=reveal(t,0,.5);
 return <SceneBase t={t} duration={duration??scene.end-scene.start} fadeOut={false}>
  <svg width={1920} height={1080} style={{position:'absolute'}}>{[0,1,2,3].map(i=><circle key={i} cx={CANOPY_ANCHOR.x} cy={CANOPY_ANCHOR.y} r={CANOPY_ANCHOR.radius+(1-p)*(550+i*190)} stroke={theme.color.terracotta} strokeWidth={1.5} fill="none" opacity={(1-p)*.65}/>)}</svg>
  <AbsoluteFill style={{opacity:p,transform:'translateY(-104px) scale(.82)',transformOrigin:'center'}}><BrandLockup seconds={12} prefix="outro"/></AbsoluteFill>
  <div style={{position:'absolute',top:696,left:144,right:144,textAlign:'center'}}><PressText text={title??scene.title[0]} t={t} delay={.3} align="center" size={theme.type.heading}/></div>
 </SceneBase>;
};
export const SCENES={S0:LogoScene,S1:WhyNow,S2:TrustPerson,S3:TreeRings,S4:Platform,S5:HongKong,S6:FirstYear,S7:Welcome};
