import React from 'react';
import {Img,staticFile} from 'remotion';
import layout from '../config/awards-stage2.json';
export const awardOffsetStage2=(t:number)=>{
 const m=layout.motion;const p=Math.max(0,Math.min(1,(t-m.initial_hold_s)/(m.duration-m.initial_hold_s-m.final_hold_s)));
 return -m.travel*(1-p);
};
export const AwardsStage2:React.FC<{t:number}>=({t})=>{
 const m=layout.motion;const p=1-Math.pow(1-Math.max(0,Math.min(1,t/.45)),4);
 return <div style={{position:'absolute',left:m.window_left,top:390,width:m.window_width,height:400,overflow:'hidden',clipPath:`inset(0 ${(1-p)*100}% 0 0)`}}>
  <div style={{position:'absolute',left:awardOffsetStage2(t),top:0,width:m.row_width,height:m.baseline_y-390}}>
   {layout.items.map(a=><Img key={a.id} src={staticFile(a.file)} style={{position:'absolute',left:a.x,bottom:0,width:a.display_width,height:a.display_height}}/>)}
  </div>
  <div style={{position:'absolute',left:0,right:0,top:m.baseline_y-390+1,height:1,background:'rgba(148,191,208,.18)'}}/>
 </div>;
};
