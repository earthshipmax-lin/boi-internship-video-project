import React from 'react';
import type {Locale} from '../config/locale-v12';
import {TextV13} from './FilmChromeV13';
import {OfficialBrandV10} from './OfficialBrandV10';
import placement from '../config/official-logo-v10.json';
const ease=(v:number)=>{const x=Math.max(0,Math.min(1,v));return x*x*(3-2*x)};
export const RootsV21:React.FC<{sourceFrame:number;locale:Locale;elapsed?:number;secondOverride?:boolean;secondElapsed?:number}>=({locale,elapsed=0,secondOverride=false,secondElapsed=0})=>{
 const t=elapsed,second=secondOverride,p=ease((second?secondElapsed:t-.62)/.4);
 const text=locale==='en'?(second?'Steady steps.\nA lasting future.':'Strong roots.\nRoom to grow.'):locale==='zh-CN'?(second?'步伐够稳，\n走得更远。':'根扎得深，\n长得更高。'):(second?'步伐夠穩，\n走得更遠。':'根扎得深，\n長得更高。');
 return <><TextV13 id="roots.title" locale={locale} size={locale==='en'?90:128} minSize={locale==='en'?82:128} lines={2} style={{left:180,top:430,width:760,fontWeight:700,lineHeight:1.18,color:'#0B2E45',whiteSpace:'pre-line',opacity:p,transform:'translateY(-50%)'}}>{text}</TextV13><div style={{position:'absolute',left:180,top:640,width:80,height:3,background:'#B9653F',opacity:p}}/>
 <div data-v21-tree="same-component-and-clock-as-closing" style={{position:'absolute',left:1060,top:150,width:700,height:560,overflow:'hidden'}}>
 {(()=>{const sourceWidth=95.75112751258398,sourceHeight=76.3045,k=Math.min(700/(sourceWidth*placement.scale),560/(sourceHeight*placement.scale));const x=(700-sourceWidth*placement.scale*k)/2-k*(placement.translateX+8.8875*placement.scale),y=(560-sourceHeight*placement.scale*k)/2-k*(placement.translateY+8.0655*placement.scale);return <div style={{position:'absolute',left:0,top:0,width:1920,height:1080,transformOrigin:'0 0',transform:`translate(${x}px,${y}px) scale(${k})`}}><OfficialBrandV10 seconds={1.2+Math.max(0,t)*2.05} prefix="roots-v21"/></div>})()}
 </div></>;
};
