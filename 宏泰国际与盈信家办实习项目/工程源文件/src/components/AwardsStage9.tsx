import React from 'react';
import {Img,staticFile} from 'remotion';
import spec from '../config/awards-stage8.json';
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
const ease=(x:number)=>1-Math.pow(1-clamp(x),4);
const minX=Math.min(...spec.items.map(a=>a.x));
const maxX=Math.max(...spec.items.map(a=>a.x+a.display_width))+55;
const sweepSpeed=(maxX-minX+700)/1.6;
// A 0.4-second linear fade lives behind the crest of the moving light mask.
const crest=100*(sweepSpeed*.4/700);
export const AwardsStage9:React.FC<{sceneTime:number}>=({sceneTime:t})=>{
 const move=clamp((t-.9)/3.7),sweepT=clamp((t-.9)/1.6),bandX=minX-700+(maxX-minX+700)*sweepT;
 let front=0,back=0;
 return <>{spec.items.map(a=>{
  const trophy=a.category==='trophy',index=trophy?front++:back++;
  // Both depth layers enter in parallel; paired back documents avoid a ten-item queue.
  const delay=(trophy?index:Math.floor(index/2))*3/30,p=ease((t-delay)/.45);
  const x=a.x+(trophy?55:18)*move,y=a.top+(trophy?24:12)*(1-p),opacity=(trophy?1:spec.back_opacity)*p;
  return <div key={a.id} data-stage9-award={a.id} data-stage9-layer={a.category} style={{position:'absolute',left:x,top:y,width:a.display_width,height:a.display_height,opacity,zIndex:trophy?1:0}}>
   <Img src={staticFile(a.file)} style={{width:'100%',height:'100%'}}/>
   {!trophy&&<div style={{position:'absolute',inset:0,background:'#061C2B',opacity:spec.back_mist_opacity}}/>}
   {t>=.9&&t<=2.5&&<Img data-stage9-sweep src={staticFile(a.file)} style={{position:'absolute',inset:0,width:'100%',height:'100%',filter:'brightness(0) invert(1)',opacity:.04,mixBlendMode:'screen',maskImage:`linear-gradient(90deg,transparent 0%,black ${crest}%,transparent 100%)`,WebkitMaskImage:`linear-gradient(90deg,transparent 0%,black ${crest}%,transparent 100%)`,maskSize:'700px 100%',WebkitMaskSize:'700px 100%',maskRepeat:'no-repeat',WebkitMaskRepeat:'no-repeat',maskPosition:`${bandX-x}px 0`,WebkitMaskPosition:`${bandX-x}px 0`}}/>}
  </div>;
 })}</>;
};
export const awardsStage9Timing={entryDone:24,lightStart:.9,lightEnd:2.5,lightWidth:700,lightPeak:.04,lightFadeSeconds:.4,backShift:18,frontShift:55,shiftStart:.9,shiftEnd:4.6} as const;
