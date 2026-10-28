import React from 'react';
import type {Locale} from '../config/locale-v12';
import {TextV13} from './FilmChromeV13';
import official from '../assets/official-logo-v10.json';
const ease=(v:number)=>{const x=Math.max(0,Math.min(1,v));return x*x*(3-2*x)};
const draw=(n:any,key:React.Key):React.ReactNode=>React.createElement(n.tag,{...n.attrs,fill:n.attrs.fill==='url(#linear-gradient1)'?'url(#roots20-gradient)':n.attrs.fill,key},n.children?.length?n.children.map((c:any,i:number)=>draw(c,i)):undefined);
export const RootsV20:React.FC<{sourceFrame:number;locale:Locale;elapsed?:number;secondOverride?:boolean;secondElapsed?:number}>=({locale,elapsed=0,secondOverride=false,secondElapsed=0})=>{
 const t=elapsed,second=secondOverride,p=ease((second?secondElapsed:t-.62)/.4),trunk=ease(t/.5);
 const text=locale==='en'?(second?'Steady steps.\nA lasting future.':'Strong roots.\nRoom to grow.'):locale==='zh-CN'?(second?'步伐够稳，\n走得更远。':'根扎得深，\n长得更高。'):(second?'步伐夠穩，\n走得更遠。':'根扎得深，\n長得更高。');
 return <><TextV13 id="roots.title" locale={locale} size={locale==='en'?90:128} minSize={locale==='en'?82:128} lines={2} style={{left:180,top:430,width:760,fontWeight:700,lineHeight:1.18,color:'#0B2E45',whiteSpace:'pre-line',opacity:p,transform:'translateY(-50%)'}}>{text}</TextV13><div style={{position:'absolute',left:180,top:640,width:80,height:3,background:'#B9653F',opacity:p}}/>
 <svg viewBox="8.8875 8.0655 95.75112751258398 76.3045" style={{position:'absolute',left:1060,top:150,width:700,height:560}}>
 <defs><linearGradient id="roots20-template" x1={1038.77} y1={-313.09} x2={1038.77} y2={-222.15} gradientTransform="translate(-1333.76 24.27) scale(.5)" gradientUnits="userSpaceOnUse"><stop offset={.51} stopColor="#007bc7"/><stop offset={.78} stopColor="#0057a9"/><stop offset={.82} stopColor="#0051a4"/></linearGradient><linearGradient id="roots20-gradient" x1={2782.26} y1={29.17} x2={2782.26} y2={120.1} href="#roots20-template"/><clipPath id="roots20-clip"><rect x={0} y={84.4-46*trunk} width={110} height={46*trunk}/></clipPath></defs>
 <g opacity={ease(t/.2)}>{draw(official.base,'base')}</g><g clipPath="url(#roots20-clip)">{draw(official.trunk,'trunk')}</g>
 {official.leaves.map((l:any,i:number)=><g key={i} opacity={ease((t-l.ring*2/30)/(.6-10/30))}>{draw(l.node,i)}</g>)}
 </svg></>;
};
