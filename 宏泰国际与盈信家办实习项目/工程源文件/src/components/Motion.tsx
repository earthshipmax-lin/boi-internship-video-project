import React from 'react';
import {AbsoluteFill,Easing,interpolate} from 'remotion';
import {theme,clamp01,reveal} from '../theme';
// Adapted from video-shotcraft PaperTitleCard.tsx: 4f stagger, 9f press,
// scale 1.28→1 + blur 7→0. No template glow, decoration, or added copy.
export const PressText:React.FC<{text:string;t:number;delay?:number;size?:number;color?:string;align?:'left'|'center';accent?:boolean}> = ({text,t,delay=0,size=theme.type.title,color=theme.color.ink,align='left',accent=false})=>{
 const p=Easing.bezier(.2,.75,.3,1)(clamp01((t-delay-4/30)/(9/30)));
 return <div style={{fontFamily:theme.font.serif,fontSize:size,fontWeight:600,lineHeight:1.28,letterSpacing:'.025em',textAlign:align,whiteSpace:'nowrap',color:accent?theme.color.terracotta:color,opacity:p,transform:`scale(${1.28-.28*p})`,transformOrigin:align==='left'?'left center':'center',filter:p<1?`blur(${(1-p)*7}px)`:undefined}}>{text}</div>;
};
export const SceneBase:React.FC<React.PropsWithChildren<{background?:string;t:number;duration:number;fadeOut?:boolean}>>=({children,background=theme.color.paper,t,duration,fadeOut=true})=>{
 const o=reveal(t,0,.4)*(fadeOut?1-reveal(t,duration-.4,.4):1);
 return <AbsoluteFill style={{background,color:theme.color.ink,fontFamily:theme.font.sans,overflow:'hidden'}}><AbsoluteFill style={{opacity:o}}>{children}</AbsoluteFill></AbsoluteFill>;
};
export const StrokePath:React.FC<{d:string;p:number;color?:string;width?:number}> = ({d,p,color=theme.color.terracotta,width=2})=><path d={d} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray="1" strokeDashoffset={1-clamp01(p)}/>;
// Normalized dash rendering adapted from video-shotcraft DrawSvgTrace.tsx.
// This project intentionally omits pen shadows, flash, card chrome and glows.
export const ringEase=(t:number)=>Easing.inOut(Easing.cubic)(clamp01(t));
export const FineRing:React.FC<{cx:number;cy:number;r:number;p:number;opacity?:number;width?:number;color?:string}>=({cx,cy,r,p,opacity=1,width=2,color=theme.color.terracotta})=><circle cx={cx} cy={cy} r={r} fill="none" stroke={color} strokeWidth={width} pathLength={1} strokeDasharray="1" strokeDashoffset={1-clamp01(p)} opacity={opacity} transform={`rotate(-90 ${cx} ${cy})`}/>;
