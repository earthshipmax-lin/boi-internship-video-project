import React from 'react';
import {AbsoluteFill} from 'remotion';
import {themeV13 as C,revealV13} from '../config/theme-v14';

/** Same annual-ring geometry/entry as Stage3, with explicit new colour tokens. */
export const BackdropV14:React.FC<{time:number;paper?:boolean;vision?:boolean;extra?:number}>=({time,paper=false,vision=false,extra=0})=>{
 const growth=vision?Math.max(0,time-3.2)*1.5:Math.min(time,66)*3;
 return <AbsoluteFill data-v13-backdrop={paper?'paper':'blue'} style={{background:paper?C.paper:`linear-gradient(180deg,${C.deep} 0%,${C.navy} 70%,${C.bottom} 100%)`}}>{!paper&&<>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse 95% 65% at 25% 45%,rgba(100,210,233,.16),transparent 75%)'}}/>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse 70% 85% at 95% 20%,rgba(4,35,65,.24),transparent 80%)'}}/><svg width={1920} height={1080} style={{position:'absolute',inset:0}}><g opacity={.10}>{Array.from({length:12+extra},(_,i)=>{const r=140+i*115+growth;return <ellipse key={i} cx={960} cy={820} rx={r} ry={r*.53} fill="none" stroke={i>=12?C.paper:i%3===0?C.paper:C.blue} strokeWidth={i>=12?1.4:i%3===0?1.1:.7} opacity={(i>=12?.82:.65-i*.025)*revealV13(time,.1+i*.05,1.8)}/>;})}</g></svg>
  <div style={{position:'absolute',left:0,right:0,top:868,height:1,background:'linear-gradient(90deg,transparent,rgba(244,238,226,.16),transparent)'}}/>
 </>}</AbsoluteFill>;
};
