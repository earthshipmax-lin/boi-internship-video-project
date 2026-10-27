import React from 'react';
import {AbsoluteFill} from 'remotion';
import {ringEaseStage4} from './RingIrisStage4';
import {stage5Timing as timing} from '../config/hk-v12-stage5';
export const RingIrisStage5:React.FC<{frame:number;oldScene:React.ReactNode;newBackground:React.ReactNode}>=({frame,oldScene,newBackground})=>{
 const p=ringEaseStage4(frame/timing.spreadFrames),r=1270*p;
 const mask=frame<=0?'radial-gradient(circle at 960px 820px, transparent 0px, transparent 1px)':`radial-gradient(circle at 960px 820px, black 0px, black ${r}px, transparent ${r+60}px)`;
 return <AbsoluteFill>
  <AbsoluteFill>{oldScene}</AbsoluteFill>
  <AbsoluteFill style={{maskImage:mask,WebkitMaskImage:mask,maskRepeat:'no-repeat',WebkitMaskRepeat:'no-repeat'}}>{newBackground}</AbsoluteFill>
  {p>0&&p<1&&<svg width={1920} height={1080} style={{position:'absolute',inset:0}}><circle cx={960} cy={820} r={r+30} fill="none" stroke="#FFFFFD" strokeWidth={2} opacity={.18*(1-p)}/></svg>}
 </AbsoluteFill>;
};
