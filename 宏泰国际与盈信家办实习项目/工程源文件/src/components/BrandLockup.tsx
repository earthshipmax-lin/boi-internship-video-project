import React from 'react';
import tree from '../assets/tree.json';
import wordmark from '../assets/wordmark.json';
import {hk} from '../config/hk';
import {progress} from '../theme';
const T=hk.logoTimeline;
export const BrandLockup:React.FC<{seconds:number;prefix?:string;chineseOnly?:boolean}> = ({seconds,prefix='boi',chineseOnly=hk.chineseOnly})=>{
 const pb=progress(seconds,T.baseStart,T.baseDur),pt=progress(seconds,T.trunkStart,T.trunkDur),pw=progress(seconds,T.wordStart,T.wordDur);
 const mid=tree.BASE.x+tree.BASE.width/2;
 return <div style={{position:'absolute',left:'50%',top:'50%',transform:'translate(-50%, -50%)',display:'flex',alignItems:'center',gap:40}}>
  <svg viewBox="25 0 120 128" width={420} height={384} style={{overflow:'visible',flexShrink:0}}>
   <defs>
    {['leafGrad','trunkGrad'].map(id=><linearGradient key={id} id={`${prefix}-${id}`} x1={0} y1={12} x2={0} y2={107} gradientUnits="userSpaceOnUse">
      <stop offset={0} stopColor={tree.COLORS.canopyTop}/><stop offset={.65} stopColor={tree.COLORS.canopyLower}/><stop offset={1} stopColor={tree.COLORS.base}/>
    </linearGradient>)}
    {tree.LEAF_CONTOURS.map((L,i)=> <linearGradient key={i} id={`${prefix}-leaf-${i}`} href={`#${prefix}-leafGrad`} gradientTransform={`rotate(${-(90-L.deg)}) translate(${-L.x} ${-L.y})`}/>)}
   </defs>
   <rect id="base" {...tree.BASE} fill={tree.COLORS.base} transform={`translate(${mid} 0) scale(${pb} 1) translate(${-mid} 0)`}/>
   <path id="trunk" d={tree.TRUNK} fill={`url(#${prefix}-trunkGrad)`} style={{clipPath:`inset(${(1-pt)*100}% 0 0 0)`}}/>
   <g id="canopy">{tree.RINGS.map((_,ring)=><g key={ring} id={`ring-${ring+1}`}>
     {tree.LEAF_CONTOURS.map((L,i)=>{
      if(L.ring!==ring)return null;
      const delay=T.leavesStart+ring*T.ringGap+Math.abs(90-L.deg)/110*.45;
      const p=progress(seconds,delay,T.leafDur),k=.2+.8*p;
      return <g key={i} transform={`translate(${L.x} ${L.y}) rotate(${90-L.deg})`}>
       <path className="leaf" d={L.d} fill={`url(#${prefix}-leaf-${i})`} opacity={p.toFixed(3)} transform={`scale(${k.toFixed(5)})`}/>
      </g>;
     })}
   </g>)}</g>
  </svg>
  <svg viewBox="150 18 270 92" width={600} height={600*92/270} style={{display:'block',flexShrink:0,opacity:pw}}>
   <defs><linearGradient id={`${prefix}-name`} x1={177} y1={0} x2={353} y2={0} gradientUnits="userSpaceOnUse"><stop offset={.35} stopColor="#175082"/><stop offset={.6} stopColor="#1e87a6"/></linearGradient>
    {[['cn',178.27,352.04,18,74],['en',160.05,375.68,92,36]].map(([id,left,right,y,h])=>{
      const w=(Number(right)-Number(left)+1)*pw;
      return <clipPath id={`${prefix}-${id}`} key={id}><rect x={((Number(left)+Number(right)-w)/2).toFixed(4)} width={w.toFixed(4)} y={Number(y)} height={Number(h)}/></clipPath>;
    })}
   </defs>
   <g clipPath={`url(#${prefix}-cn)`}>{wordmark['chinese-glyphs'].map(L=><path key={L.id} d={L.d} fill={`url(#${prefix}-name)`}/>)}</g>
   {!chineseOnly&&<g clipPath={`url(#${prefix}-en)`}>{wordmark['english-glyphs'].map(L=><path key={L.id} d={L.d} fill="#245e91"/>)}</g>}
  </svg>
 </div>;
};
// Shared anchor derived from the approved SVG viewBox and the existing flex layout.
// Native SVG meet scaling: 384/128 = 3, 30px horizontal letterboxing.
export const CANOPY_ANCHOR={x:430+30+(84.5-25)*3,y:348+70.5*3,radius:56*3};
