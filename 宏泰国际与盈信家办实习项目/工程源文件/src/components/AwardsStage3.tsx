import React from 'react';
import {Img,staticFile} from 'remotion';
import spec from '../config/awards-stage3.json';
const ease=(v:number)=>1-Math.pow(1-Math.max(0,Math.min(1,v)),4);
export const AwardsStage3:React.FC<{t:number}>=({t})=><>
 <div style={{position:'absolute',inset:0,opacity:spec.back_opacity*ease((t-spec.back_delay_seconds)/spec.back_entry_seconds)}}>
  {spec.items.filter(a=>a.category==='document').map(a=><div key={a.id} style={{position:'absolute',left:a.x,top:a.top,width:a.display_width,height:a.display_height}}>
   <Img src={staticFile(a.file)} style={{width:'100%',height:'100%'}}/>
   <div style={{position:'absolute',inset:0,background:'#061C2B',opacity:spec.back_mist_opacity}}/>
  </div>)}
 </div>
 {spec.items.filter(a=>a.category==='trophy').map((a,i)=>{const p=ease((t-i*5/30)/.5);return <Img key={a.id} src={staticFile(a.file)} style={{position:'absolute',left:a.x,top:a.top+24*(1-p),width:a.display_width,height:a.display_height,opacity:p}}/>;})}
 <div style={{position:'absolute',left:130,right:130,top:1042,height:1,background:'rgba(148,191,208,.2)'}}/>
 <div style={{position:'absolute',left:130,top:1050,fontFamily:'Noto Sans TC',fontSize:14,letterSpacing:1,color:'#F4EEE2',opacity:.55}}>資料來源：公司介紹</div>
</>;
