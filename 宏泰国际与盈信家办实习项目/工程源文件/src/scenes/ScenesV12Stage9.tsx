import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,Audio,Img,staticFile,useCurrentFrame,delayRender,continueRender} from 'remotion';
import {EpicFilmV12Offices} from './ScenesV12Offices';
import {BackdropStage3} from './ScenesV12Stage3';
import {AwardsStage9} from '../components/AwardsStage9';
import {GeographicNetworkStage9} from '../components/GeographicNetworkStage9';
import {PlatformStage9} from '../components/PlatformStage9';
import {RingIrisStage5} from '../components/RingIrisStage5';
import {epicV12Stage5} from '../config/hk-v12-stage5';
import {stage9 as t} from '../config/stage9';
import captions from '../config/captions-v12-stage3.json';
const C=epicV12Stage5.colors;
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const ease=(v:number)=>1-Math.pow(1-clamp(v),4);
const Brand:React.FC=()=><div style={{position:'absolute',top:66,left:112,width:330,height:92,opacity:.86}}><Img src={staticFile('brand/v10/宏泰.svg')} style={{width:'100%',height:'100%',objectFit:'contain',filter:'brightness(0) invert(1) drop-shadow(0 0 9px rgba(77,177,224,.26))'}}/></div>;
const Meta:React.FC<{children:React.ReactNode}>=({children})=><div data-final-meta style={{position:'absolute',top:94,right:112,fontFamily:'Noto Sans TC',fontSize:20,fontWeight:500,letterSpacing:3,color:C.paper,opacity:.65}}>{children}</div>;
const Title:React.FC<{time:number;top:number;size:number;children:React.ReactNode}>=({time,top,size,children})=>{const p=ease(time/.85);return <div style={{position:'absolute',left:130,top,fontFamily:'Noto Sans TC',fontWeight:800,fontSize:size,letterSpacing:'-.055em',lineHeight:1.12,opacity:p,transform:`translateY(${35*(1-p)}px)`}}>{children}</div>;};
const Footer:React.FC<{frame:number;watermark:boolean;paper:boolean}>=({frame,watermark,paper})=>{
 const time=Math.min(frame/30,68.1),caption=captions.find(c=>time>=c.start&&time<c.end+.12);
 return <><div data-final-caption style={{position:'absolute',left:105,right:105,bottom:58,textAlign:'center',height:55,fontFamily:'Noto Sans TC',fontWeight:500,fontSize:36,letterSpacing:1,color:paper?C.deep:C.paper,textShadow:paper?'none':'0 2px 12px rgba(0,0,0,.7)',opacity:caption?1:0}}>{caption?.text}</div>
 {watermark&&<div data-final-watermark style={{position:'absolute',left:114,bottom:26,fontFamily:'Noto Sans TC',fontSize:16,letterSpacing:2,color:paper?C.deep:C.paper,opacity:.45}}>內部審片版 · 不作對外發布</div>}</>;
};
const PlatformSnapshot:React.FC=()=><AbsoluteFill style={{color:C.paper}}><BackdropStage3 t={2.8}/><PlatformStage9 sceneTime={(t.irisStart-t.platformStart)/30}/><Brand/><Meta>家族辦公室平台</Meta></AbsoluteFill>;
export const EpicFilmV12Stage9:React.FC<{watermark?:boolean;qa?:boolean}>=({watermark=true,qa=false})=>{
 const frame=useCurrentFrame(),time=frame/30,active=frame>=t.awardsStart&&frame<t.officeStart,root=useRef<HTMLDivElement>(null);
 const phase=frame<t.awardsEnd?'awards':frame<t.mapEnd?'map':frame<t.irisStart?'platform':'iris';
 useLayoutEffect(()=>{if(!qa)return;const handle=delayRender('Stage9 layout audit');let raf=0,done=false;
  const measure=()=>{if(!root.current)return;const el=root.current,b=el.getBoundingClientRect();const box=(e:Element)=>{const r=e.getBoundingClientRect();return {x:r.x-b.x,y:r.y-b.y,width:r.width,height:r.height};};
   const caption=el.querySelector('[data-final-caption]');
   const awards=Array.from(el.querySelectorAll('[data-stage9-award]')).map(e=>({id:e.getAttribute('data-stage9-award'),layer:e.getAttribute('data-stage9-layer'),rect:box(e),opacity:getComputedStyle(e).opacity}));
   const platform=Array.from(el.querySelectorAll('[data-stage9-platform]')).map(e=>({role:e.getAttribute('data-stage9-platform'),id:e.getAttribute('data-id'),rect:box(e),opacity:getComputedStyle(e).opacity}));
   console.log('STAGE9_AUDIT:'+JSON.stringify({frame,phase,active,root:{width:b.width,height:b.height},text:el.innerText,caption:caption?.textContent,captionRect:caption?box(caption):null,watermark:!!el.querySelector('[data-final-watermark]'),awards,sweeps:el.querySelectorAll('[data-stage9-sweep]').length,platform}));done=true;continueRender(handle);};
  raf=requestAnimationFrame(()=>{raf=requestAnimationFrame(measure);});return()=>{cancelAnimationFrame(raf);if(!done)continueRender(handle);};
 },[frame,qa,active,phase]);
 return <AbsoluteFill ref={root} style={{width:1920,height:1080}}>{!active?<EpicFilmV12Offices watermark={watermark}/>:<AbsoluteFill style={{color:C.paper,background:C.deep}}>
  {phase==='iris'?<RingIrisStage5 frame={frame-t.irisStart} oldScene={<PlatformSnapshot/>} newBackground={<BackdropStage3 t={0} paper/>}/>:<>
   <BackdropStage3 t={phase==='awards'?Math.min(1,(frame-t.awardsStart)/30):phase==='map'?4:Math.min(2.8,(frame-t.platformStart)/30)}/>
   {phase==='awards'?<><Brand/><Meta>專業的積累</Meta><Title time={(frame-t.awardsStart)/30} top={174} size={88}>每一份信任，都有分量。</Title><div style={{position:'absolute',left:134,top:280,fontFamily:'Noto Sans TC',fontSize:23,fontWeight:500,letterSpacing:2,opacity:.65}}>業界肯定，見證專業積累</div><AwardsStage9 sceneTime={(frame-t.awardsStart)/30}/></>:phase==='map'?<>
    <GeographicNetworkStage9 time={time} sceneTime={(frame-t.mapStart)/30} qa={qa}/><Brand/><Meta>全球視野 · 一路向前</Meta><Title time={(frame-t.mapStart)/30} top={190} size={96}>讓眼光，跨越地域。</Title>
   </>:<><PlatformStage9 sceneTime={(frame-t.platformStart)/30} qa={qa}/><Brand/><Meta>家族辦公室平台</Meta></>}
  </>}
  <Footer frame={frame} watermark={watermark} paper={phase==='iris'&&frame>=1336}/><Audio src={staticFile(epicV12Stage5.mix)}/>
 </AbsoluteFill>}</AbsoluteFill>;
};
