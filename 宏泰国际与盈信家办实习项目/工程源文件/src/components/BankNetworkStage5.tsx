import React from 'react';
import {Img,staticFile} from 'remotion';
import {bankDisplayStage5 as g} from '../config/hk-v12-stage5';
const ease=(x:number)=>1-Math.pow(1-Math.max(0,Math.min(1,x)),4);
export const BankNetworkStage5:React.FC<{t:number}>=({t})=>{
 const p=ease((t-.35)/.45);
 return <div style={{position:'absolute',inset:0,opacity:p}}>
  <div style={{position:'absolute',left:g.left,top:g.headingTop,fontFamily:'Noto Sans TC',fontSize:19,fontWeight:500,letterSpacing:2,color:'#F4EEE2',opacity:.78}}>銀行服務網絡 · 據公司資料</div>
  <div style={{position:'absolute',left:g.left,top:g.top,width:g.width,height:g.height,background:'#FFFFFF',overflow:'hidden'}}>
   <div style={{position:'absolute',left:g.width/2,top:24,bottom:24,width:1,background:'rgba(6,28,43,.13)'}}/>
   {g.items.map((a,i)=>{
    const [x0,y0,x1,y1]=a.ink,scale=g.visualInkHeight/(y1-y0);
    const cx=g.width*(i+.5)/2,cy=g.height/2;
    const left=cx-(x0+x1)*scale/2,top=cy-(y0+y1)*scale/2;
    const clip=[Math.max(0,y0-g.sourceMargin),Math.max(0,a.sourceWidth-x1-g.sourceMargin),Math.max(0,a.sourceHeight-y1-g.sourceMargin),Math.max(0,x0-g.sourceMargin)].map(v=>`${v*scale}px`).join(' ');
    return <Img key={a.id} src={staticFile(a.file)} style={{position:'absolute',left,top,width:a.sourceWidth*scale,height:a.sourceHeight*scale,clipPath:`inset(${clip})`}}/>;
   })}
  </div>
 </div>;
};
