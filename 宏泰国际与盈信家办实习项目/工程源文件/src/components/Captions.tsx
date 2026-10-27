import React from 'react';
import {useCurrentFrame,useVideoConfig} from 'remotion';
import {hk,type SceneSpec} from '../config/hk';
import {theme,reveal} from '../theme';
import type {MediaAssets} from '../media';
export const cueTimings=(scene:SceneSpec,assets:MediaAssets)=>{
 const slot=scene.end-scene.start;
 const actual=scene.vo?assets[scene.vo]?.duration:undefined;
 const tail=scene.id==='S7'?0:hk.subtitle.tail;
 const duration=Math.min(actual??(slot-hk.subtitle.leadIn-tail),slot-hk.subtitle.leadIn-tail);
 const measured=scene.vo?hk.voiceTimings[scene.vo as keyof typeof hk.voiceTimings]:undefined;
 if(measured&&actual&&Math.abs(actual-measured.duration)<.05){
  const scale=duration/actual;
  return measured.chunks.map((cue,i)=>({text:cue.text,start:hk.subtitle.leadIn+cue.start*scale,
   end:scene.id==='S7'&&i===measured.chunks.length-1?slot:hk.subtitle.leadIn+(measured.chunks[i+1]?.start??measured.duration)*scale}));
 }
 const chunks=scene.subtitleChunks??[]; const total=chunks.reduce((a,b)=>a+b.length,0);let cursor=hk.subtitle.leadIn;
 return chunks.map(text=>{const start=cursor;cursor+=duration*text.length/total;return {text,start,end:cursor};});
};
export const CaptionTrack:React.FC<{scene:SceneSpec;assets:MediaAssets}> = ({scene,assets})=>{
 const t=useCurrentFrame()/useVideoConfig().fps;
 const cues=cueTimings(scene,assets); const cue=cues.find(c=>t>=c.start&&t<c.end);
 if(!cue)return null;
 // The Chinese closing headline already serves as the final welcome subtitle.
 if(scene.id==='S7'&&cue.text.replace(/[，。！？]/g,'')===scene.title[0])return null;
 const o=Math.min(reveal(t,cue.start,.16),scene.id==='S7'?1:reveal(cue.end-t,0,.12));
 return <div style={{position:'absolute',bottom:theme.space.captionBottom,left:144,right:144,textAlign:'center',fontFamily:theme.font.sans,fontWeight:400,fontSize:43,lineHeight:1.5,color:theme.color.ink,opacity:o}}><span style={{display:'inline',background:theme.color.paper,padding:'8px 24px',boxDecorationBreak:'clone'}}>{cue.text}</span></div>;
};
export const VoiceStatus:React.FC<{scene:SceneSpec;assets:MediaAssets}> = ({scene,assets})=>scene.vo&&!assets[scene.vo]?<div style={{position:'absolute',right:56,top:40,fontFamily:theme.font.sans,fontSize:24,color:theme.color.muted}}>{hk.labels.noVoice}</div>:null;
