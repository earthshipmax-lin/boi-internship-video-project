import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,Audio,Img,staticFile,useCurrentFrame,delayRender,continueRender} from 'remotion';
import {EpicFilmV12Final} from './ScenesV12Final';
import {BackdropStage3} from './ScenesV12Stage3';
import {epicV12Stage5} from '../config/hk-v12-stage5';
import {officesV12 as t} from '../config/offices-v12';
import assets from '../config/offices-assets-v12.json';
import captions from '../config/captions-v12-stage3.json';
const C=epicV12Stage5.colors;
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const ease=(v:number)=>1-Math.pow(1-clamp(v),4);
const font:React.CSSProperties={fontFamily:'Noto Sans TC',color:C.deep};
const Brand:React.FC=()=><div style={{position:'absolute',top:66,left:112,width:330,height:92,opacity:.9}}><Img src={staticFile('brand/v10/宏泰.svg')} style={{width:'100%',height:'100%',objectFit:'contain'}}/></div>;
const Meta:React.FC<{trust:boolean}>=({trust})=><div data-final-meta style={{position:'absolute',top:94,right:112,...font,fontSize:20,fontWeight:500,letterSpacing:3,opacity:.65}}>{trust?'專業為本 · 穩健為根':'三城辦公室 · 公司實景'}</div>;
type City=typeof assets.cities[number];
const Photos:React.FC<{city:City;frame:number;start:number;outgoing?:boolean;lastExit?:boolean}>=({city,frame,start,outgoing=false,lastExit=false})=><>
 {city.images.map((a,i)=>{
  const r=t.tiles[i],p=ease((frame-start-t.photoEntryDelay-i*t.tileStaggerFrames)/t.photoWipeFrames);
  const exit=outgoing?ease((frame-start-t.photoExitDelay-i*t.tileStaggerFrames)/t.photoWipeFrames):lastExit?ease((frame-t.finalExitStart)/(t.finalExitFrames-1)):0;
  const inset=outgoing||lastExit?`inset(0 0 ${exit*100}% 0)`:`inset(${(1-p)*100}% 0 0 0)`;
  return <div key={a.id} data-office-tile={a.id} data-office-visible={!(outgoing||lastExit)?p>0:exit<1} style={{position:'absolute',left:r.x,top:r.y,width:r.width,height:r.height,overflow:'hidden',clipPath:inset}}>
   <Img data-office-img={a.id} src={staticFile(a.file)} style={{width:'100%',height:'100%',objectFit:'cover',objectPosition:a.object_position,filter:assets.photo_filter,transform:`scale(${outgoing||lastExit?1:1.04-.04*p})`,transformOrigin:'center'}}/>
  </div>;
 })}
</>;
const OfficePage:React.FC<{frame:number}>=({frame})=>{
 const index=Math.min(2,t.cityStarts.filter(s=>frame>=s).length-1),city=assets.cities[index],start=t.cityStarts[index];
 const change=ease((frame-start)/t.cityChangeFrames),lastExit=frame>=t.finalExitStart,exit=lastExit?ease((frame-t.finalExitStart)/(t.finalExitFrames-1)):0;
 const initial=ease((frame-t.start)/12),nameOpacity=(1-exit),header=index===2?'眼光，跨越地域。':'看得全面。行得長遠。';
 return <>
  <div data-office-headline style={{position:'absolute',left:130,top:t.titleTop,width:1660,height:t.headlineHeight,...font,fontSize:t.titleSize,fontWeight:800,letterSpacing:'-.055em',lineHeight:1.12,opacity:initial*(1-exit)}}>{header}</div>
  <div data-office-text-region style={{position:'absolute',left:t.textRegion.x,top:t.textRegion.y,width:t.textRegion.width,height:t.textRegion.height,overflow:'hidden',...font,opacity:initial*nameOpacity}}>
   <div data-office-text-block="index" style={{position:'absolute',top:130,left:0,fontSize:20,lineHeight:'24px',color:'#7A8A93',letterSpacing:3}}>{String(index+1).padStart(2,'0')} / 03</div>
   <div data-office-name-clip style={{position:'absolute',left:0,top:160,width:430,height:160,overflow:'hidden'}}>
    {index>0&&change<1&&<div data-office-name="outgoing" style={{position:'absolute',left:0,top:10,width:430,height:145,fontSize:128,fontWeight:700,lineHeight:1.1,letterSpacing:'-.035em',opacity:1-change,transform:`translateY(${-40*change}px)`}}>{assets.cities[index-1].name}</div>}
    <div data-office-name="current" style={{position:'absolute',left:0,top:10,width:430,height:145,fontSize:128,fontWeight:700,lineHeight:1.1,letterSpacing:'-.035em',opacity:change,transform:`translateY(${40*(1-change)}px)`}}>{city.name}</div>
   </div>
   <div data-office-text-block="english" style={{position:'absolute',left:0,top:338,width:430,height:36,fontSize:26,letterSpacing:8,lineHeight:'36px'}}>{city.english}</div>
   <div data-office-text-block="address" style={{position:'absolute',left:0,top:382,width:430,height:34,fontSize:24,color:'#41596B',lineHeight:'34px'}}>{city.address}</div>
   <div data-office-text-block="progress" style={{position:'absolute',left:0,top:460,width:430,height:66}}>
    {assets.cities.map((a,i)=><div key={a.id} style={{position:'absolute',left:i*145,top:0,width:120,fontSize:20,letterSpacing:2,color:i===index?C.blue:C.deep,opacity:i===index?1:.35}}>{a.name}<div style={{position:'absolute',left:0,top:43,width:120,height:2,background:'#A9B6BD'}}><div style={{width:120*(i<index?1:i===index?change:0),height:2,background:C.blue}}/></div></div>)}
   </div>
  </div>
  <div data-office-photo-region style={{position:'absolute',left:t.photoRegion.x,top:t.photoRegion.y,width:t.photoRegion.width,height:t.photoRegion.height,pointerEvents:'none'}}/>
  {index>0&&frame<start+23&&<Photos city={assets.cities[index-1]} frame={frame} start={start} outgoing/>}
  <Photos city={city} frame={frame} start={start} lastExit={lastExit}/>
 </>;
};
const TrustPage:React.FC<{frame:number}>=({frame})=>{
 const p=ease((frame-t.trustStart)/18),out=1-ease((frame-1644)/8);
 return <div style={{position:'absolute',inset:0,opacity:out}}>
  <div data-trust-headline style={{position:'absolute',left:130,top:360,...font,fontSize:143,fontWeight:800,letterSpacing:'-.055em',lineHeight:1.12,opacity:p,transform:`translateY(${18*(1-p)}px)`}}>信任，扎根時間。</div>
 </div>;
};
const Footer:React.FC<{frame:number;watermark:boolean}>=({frame,watermark})=>{
 const time=Math.min(frame/30,68.1),caption=captions.find(c=>time>=c.start&&time<c.end+.12),trust=frame>=t.trustStart;
 return <>
  <div data-final-caption style={{position:'absolute',left:105,right:105,bottom:58,textAlign:'center',height:55,...font,fontWeight:500,fontSize:36,letterSpacing:1,opacity:caption?1:0}}>{caption?.text}</div>
  {trust?<div data-office-legal style={{position:'absolute',left:t.legal.left,top:t.legal.top,width:t.legal.width,height:t.legal.height,...font,fontSize:t.legal.fontSize,lineHeight:`${t.legal.lineHeight}px`,letterSpacing:1,opacity:t.legal.opacity*ease((frame-t.trustStart)/11)}}>
   <div>保監局持牌 FB1681 · PIBA會員 M0573{watermark&&<span data-final-watermark>　｜　內部審片版 · 不作對外發布</span>}</div>
   <div>全面風險管理 · 合規操作準則 · 客戶隱私保護 · 業務持續運營</div>
  </div>:watermark&&<div data-final-watermark style={{position:'absolute',left:114,bottom:26,...font,fontSize:16,letterSpacing:2,opacity:.45}}>內部審片版 · 不作對外發布</div>}
 </>;
};
const rect=(el:Element)=>{const r=el.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};};
export const EpicFilmV12Offices:React.FC<{watermark?:boolean;qa?:boolean}>=({watermark=true,qa=false})=>{
 const frame=useCurrentFrame(),active=frame>=t.start&&frame<t.rootsStart,trust=frame>=t.trustStart,root=useRef<HTMLDivElement>(null);
 useLayoutEffect(()=>{if(!qa)return;const handle=delayRender('Office layout audit');let done=false,raf=0;const measure=()=>{if(!root.current)return;const el=root.current,base=el.getBoundingClientRect(),read=(e:Element)=>{const r=rect(e);return {...r,x:r.x-base.x,y:r.y-base.y};},caption=el.querySelector('[data-final-caption]') as HTMLElement|null;
  const region=(s:string)=>{const e=el.querySelector(s);return e?read(e):null;};
  const text=Array.from(el.querySelectorAll('[data-office-text-block], [data-office-name]')).map(e=>({role:e.getAttribute('data-office-text-block')||e.getAttribute('data-office-name'),rect:read(e),opacity:getComputedStyle(e).opacity,text:e.textContent}));
  const tiles=Array.from(el.querySelectorAll('[data-office-tile]')).map(e=>({id:e.getAttribute('data-office-tile'),rect:read(e),visible:e.getAttribute('data-office-visible')==='true',clip:getComputedStyle(e).clipPath,rawImage:read(e.querySelector('img')!)}));
  const legal=el.querySelector('[data-office-legal]');
  console.log('OFFICES_AUDIT:'+JSON.stringify({frame,active,trust,rootRect:{x:base.x,y:base.y,width:base.width,height:base.height},text:el.innerText,caption:caption?.textContent,captionRect:caption?read(caption):null,watermark:!!el.querySelector('[data-final-watermark]'),textRegion:region('[data-office-text-region]'),photoRegion:region('[data-office-photo-region]'),nameClip:region('[data-office-name-clip]'),headline:region('[data-office-headline]'),trustHeadline:region('[data-trust-headline]'),legal:legal?{rect:read(legal),opacity:getComputedStyle(legal).opacity,fontSize:getComputedStyle(legal).fontSize}:null,textBlocks:text,tiles}));
 done=true;continueRender(handle);};raf=requestAnimationFrame(()=>{raf=requestAnimationFrame(measure);});return()=>{cancelAnimationFrame(raf);if(!done)continueRender(handle);};},[frame,qa,active,trust]);
 return <AbsoluteFill ref={root} style={{width:1920,height:1080}}>{active?<AbsoluteFill style={{background:C.paper,color:C.deep}}>
  <BackdropStage3 t={0} paper/><Brand/><Meta trust={trust}/>
  {trust?<TrustPage frame={frame}/>:<OfficePage frame={frame}/>}
  <Footer frame={frame} watermark={watermark}/><Audio src={staticFile(epicV12Stage5.mix)}/>
 </AbsoluteFill>:<EpicFilmV12Final watermark={watermark}/>}</AbsoluteFill>;
};
