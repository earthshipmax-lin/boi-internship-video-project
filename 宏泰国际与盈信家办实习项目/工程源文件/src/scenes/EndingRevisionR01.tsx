import React from 'react';
import {AbsoluteFill,Audio,Img,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {OfficialBrandV10} from '../components/OfficialBrandV10';
import {SceneV11} from './ScenesV11';
import {epicScenes,epicV11} from '../config/hk-v11';
import captions from '../config/captions-ending-r01.json';
const C=epicV11.colors;
const ease=(v:number)=>1-Math.pow(1-Math.max(0,Math.min(1,v)),4);
export const ClosingRevisionR01:React.FC=()=>{
 const t=Math.min(useCurrentFrame()/30,7.4);
 return <AbsoluteFill style={{background:C.paper,color:C.deep}}>
  <div style={{position:'absolute',inset:0,transform:'translateY(-110px)'}}>
   <OfficialBrandV10 seconds={t*2.4} prefix="closing-r01"/>
  </div>
  <div style={{position:'absolute',left:365,top:616,width:1190,height:155,opacity:ease((t-.16)/.8),transform:`translateY(${(1-ease((t-.16)/.8))*13}px)`}}>
   <Img src={staticFile('brand/closing-r01/slogan-brush.svg')} style={{width:'100%',height:'100%',objectFit:'contain'}}/>
  </div>
  <div style={{position:'absolute',left:718,top:804,display:'flex',alignItems:'center',gap:32,opacity:ease((t-3.8)/.8)}}>
   <span style={{fontSize:45,fontWeight:300,color:C.copper}}>×</span>
   <Img src={staticFile('brand/v11/evergreen.svg')} style={{width:380,height:107,objectFit:'contain'}}/>
  </div>
 </AbsoluteFill>;
};
// Reuse v11 scenes without editing their source. Only the closing scene and mix differ.
export const EpicEndingRevisionR01:React.FC=()=>{
 const t=Math.min(useCurrentFrame()/30,66);
 const caption=captions.find(c=>t>=c.start&&t<c.end+.12);
 const active=epicScenes.filter(s=>t>=s.start).at(-1);
 const paper=active?['office','roots','close'].includes(active.id):false;
 return <AbsoluteFill style={{background:C.deep}}>
  {epicScenes.map(s=><Sequence key={s.id} from={Math.round(s.start*30)} durationInFrames={Math.min(2040-Math.round(s.start*30),Math.round((s.end-s.start+.4)*30))}>
   {s.id==='close'?<ClosingRevisionR01/>:<SceneV11 id={s.id} duration={s.end-s.start}/>}
  </Sequence>)}
  <div style={{position:'absolute',left:105,right:105,bottom:58,textAlign:'center',height:55,fontFamily:'Noto Sans TC',fontWeight:500,fontSize:36,letterSpacing:1,color:paper?C.deep:C.paper,textShadow:paper?'none':'0 2px 12px rgba(0,0,0,.7)',opacity:caption?1:0}}>{caption?.text}</div>
  <div style={{position:'absolute',left:114,bottom:26,fontFamily:'Noto Sans TC',fontSize:16,letterSpacing:2,color:paper?C.deep:C.paper,opacity:.45}}>內部審片版 · 不作對外發布</div>
  <Audio src={staticFile('music/closing-r01/review-mix.wav')}/>
 </AbsoluteFill>;
};
