import React from 'react';
import {AbsoluteFill} from 'remotion';
import {irisStage4 as g} from '../config/hk-v12-stage4';
export const ringEaseStage4=(x:number)=>{
 const v=Math.max(0,Math.min(1,x));if(v===0||v===1)return v;
 let lo=0,hi=1;
 for(let i=0;i<24;i++){const t=(lo+hi)/2;const bx=3*(1-t)*(1-t)*t*.65+3*(1-t)*t*t*.35+t*t*t;if(bx<v)lo=t;else hi=t;}
 const t=(lo+hi)/2;return 3*t*t-2*t*t*t;
};
export const RingIrisStage4:React.FC<{frame:number;oldScene:React.ReactNode;newBackground:React.ReactNode;paper:boolean}>=({frame,oldScene,newBackground,paper})=>{
 const p=ringEaseStage4(frame/g.spreadFrames),r=g.radius*p;
 // Radius denotes the fully covered interior. The 60px feather extends
 // OUTSIDE it, so radius 1270 fully covers the 1263px farthest corner.
 const mask=frame<=0?'radial-gradient(circle at 960px 820px, transparent 0px, transparent 1px)':`radial-gradient(circle at ${g.cx}px ${g.cy}px, black 0px, black ${r}px, transparent ${r+g.feather}px)`;
 return <AbsoluteFill>
  <AbsoluteFill style={{transform:`scale(${1+.03*p})`,transformOrigin:`${g.cx}px ${g.cy}px`}}>{oldScene}</AbsoluteFill>
  <AbsoluteFill style={{maskImage:mask,WebkitMaskImage:mask,maskRepeat:'no-repeat',WebkitMaskRepeat:'no-repeat'}}>{newBackground}</AbsoluteFill>
  {p>0&&p<1&&<svg width={1920} height={1080} style={{position:'absolute',inset:0}}><circle cx={g.cx} cy={g.cy} r={r+g.feather/2} fill="none" stroke={paper?'#FFFFFD':'#073141'} strokeWidth={g.edgeWidth} opacity={.6*(1-p)}/></svg>}
 </AbsoluteFill>;
};
