import React from 'react';
import {Img,staticFile} from 'remotion';
export const photoEase=(x:number)=>1-Math.pow(1-Math.max(0,Math.min(1,x)),4);
export const PhotoBand:React.FC<{file:string;t:number;end?:number;style:React.CSSProperties;fit?:'contain'|'cover';logo?:boolean}>=({file,t,end=100,style,fit='contain',logo=false})=>{
 const a=photoEase(t/.45),b=photoEase((t-end+.45)/.45);
 return <div style={{position:'absolute',overflow:'hidden',clipPath:`inset(0 ${(1-a)*100}% 0 ${b*100}%)`,...style}}>
  <Img src={staticFile(file)} style={{width:'100%',height:'100%',objectFit:fit,transform:logo?'none':`scale(${1.06-.06*a})`,transformOrigin:'center center',filter:logo?'none':'contrast(1.06) saturate(.92)'}}/>
  {!logo&&<div style={{position:'absolute',inset:0,background:'rgba(11,46,69,.08)',mixBlendMode:'multiply'}}/>}
 </div>;
};
