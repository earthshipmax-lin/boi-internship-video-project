import React,{useLayoutEffect,useRef} from 'react';
import {Img,staticFile,delayRender,continueRender} from 'remotion';
import spec from '../config/awards-stage8.json';
import type {Locale} from '../config/locale-v12';

export type AwardsColorsStage10={deep:string;navy:string;paper:string};
export const awardsColorsStage10: AwardsColorsStage10={deep:'#0B314A',navy:'#0F4668',paper:'#F4EEE2'};
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
const ease=(x:number)=>1-Math.pow(1-clamp(x),4);
const docPositions:Record<string,number>={'native-a004':190,'native-a005':1600,'native-a012':570,'native-a013':800,'native-a014':1000,'native-a015':1200};
export const awardCoupletLabelsStage10={
 'native-a004':{yue:'永明金融 SUN LIFE','zh-CN':'永明金融 SUN LIFE',en:'Sun Life'},
 'native-a005':{yue:'友邦 AIA','zh-CN':'友邦 AIA',en:'AIA'},
} as const;
// Source order stays unchanged, preserving all six document and four trophy
// per-layer indices. Only the six rear x positions are replaced.
export const awardsLayoutStage10=spec.items.map(a=>({...a,x:a.category==='document'?docPositions[a.id]:a.x}));
export const awardsTimingStage10={entryDone:.8,lightStart:.9,lightEnd:2.5,lightWidth:700,lightPeak:.04,lightFadeSeconds:.4,backShift:18,frontShift:55,shiftStart:.9,shiftEnd:4.6} as const;
export const awardStateStage10=(sceneTime:number)=>{
 let front=0,back=0;const move=clamp((sceneTime-.9)/3.7);
 return awardsLayoutStage10.map(a=>{
  const trophy=a.category==='trophy',index=trophy?front++:back++;
  const delay=(trophy?index:Math.floor(index/2))*3/30,p=ease((sceneTime-delay)/.45);
  return {...a,index,delay,progress:p,x:a.x+(trophy?55:18)*move,y:a.top+(trophy?24:12)*(1-p),opacity:(trophy?1:spec.back_opacity)*p,
   label:a.id in awardCoupletLabelsStage10?{x:a.x+18*move+(a.display_width-250)/2,y:a.top+12*(1-p)+a.display_height+12,width:250,height:22,opacity:.72*p}:null};
 });
};
const minX=Math.min(...awardsLayoutStage10.map(a=>a.x));
const maxX=Math.max(...awardsLayoutStage10.map(a=>a.x+a.display_width))+55;
const sweepSpeed=(maxX-minX+700)/1.6,crest=100*(sweepSpeed*.4/700);

/** The six rear documents are rearranged; original source pixels and all four
 * foreground trophy geometries remain unchanged. Parent owns scene branding,
 * background, captions and audio. */
export const AwardsStage10:React.FC<{sceneTime:number;locale?:Locale;qa?:boolean;colors?:Partial<AwardsColorsStage10>}>=({sceneTime:t,locale='yue',qa=false,colors={}})=>{
 const root=useRef<HTMLDivElement>(null),palette={...awardsColorsStage10,...colors};
 const items=awardStateStage10(t),bandX=minX-700+(maxX-minX+700)*clamp((t-.9)/1.6);
 useLayoutEffect(()=>{
  if(!qa)return;const handle=delayRender('Stage10 awards text and layer audit');let raf=0,done=false;
  const measure=()=>{
   if(!root.current)return;const base=root.current.getBoundingClientRect(),scale=base.width/1920;
   const read=(e:Element)=>{const r=e.getBoundingClientRect();return {x:(r.x-base.x)/scale,y:(r.y-base.y)/scale,width:r.width/scale,height:r.height/scale};};
   const awards=Array.from(root.current.querySelectorAll('[data-stage10-award]')).map(e=>({id:e.getAttribute('data-stage10-award'),layer:e.getAttribute('data-stage10-layer'),rect:read(e),opacity:getComputedStyle(e).opacity,zIndex:getComputedStyle(e).zIndex}));
   const labels=Array.from(root.current.querySelectorAll('[data-stage10-award-label]')).map(e=>{
    const range=document.createRange();range.selectNodeContents(e);const r=range.getBoundingClientRect(),style=getComputedStyle(e);
    return {id:e.getAttribute('data-stage10-award-label'),text:e.textContent,rect:read(e),ink:{x:(r.x-base.x)/scale,y:(r.y-base.y)/scale,width:r.width/scale,height:r.height/scale},fontFamily:style.fontFamily,fontSize:style.fontSize,letterSpacing:style.letterSpacing,opacity:style.opacity,zIndex:style.zIndex};
   });
   console.log('STAGE10_AWARDS:'+JSON.stringify({sceneTime:t,locale,colors:palette,root:{width:base.width,height:base.height},awards,labels,retainedDocuments:6,retainedTrophies:4,sourceCheck:'qa/v12/stage10/COUPLET_SOURCE_CHECK.md'}));done=true;continueRender(handle);
  };
  raf=requestAnimationFrame(()=>{raf=requestAnimationFrame(measure);});return()=>{cancelAnimationFrame(raf);if(!done)continueRender(handle);};
 },[t,locale,qa,palette.deep,palette.navy,palette.paper]);
 return <div ref={root} style={{position:'absolute',inset:0}}>{items.map(a=>{
  const trophy=a.category==='trophy',label=a.label;
  return <React.Fragment key={a.id}>
   <div data-stage10-award={a.id} data-stage10-layer={a.category} style={{position:'absolute',left:a.x,top:a.y,width:a.display_width,height:a.display_height,opacity:a.opacity,zIndex:trophy?1:0}}>
    <Img src={staticFile(a.file)} style={{width:'100%',height:'100%'}}/>
    {!trophy&&<div style={{position:'absolute',inset:0,background:palette.deep,opacity:spec.back_mist_opacity}}/>}
    {t>=.9&&t<=2.5&&<Img data-stage10-sweep src={staticFile(a.file)} style={{position:'absolute',inset:0,width:'100%',height:'100%',filter:'brightness(0) invert(1)',opacity:.04,mixBlendMode:'screen',maskImage:`linear-gradient(90deg,transparent 0%,black ${crest}%,transparent 100%)`,WebkitMaskImage:`linear-gradient(90deg,transparent 0%,black ${crest}%,transparent 100%)`,maskSize:'700px 100%',WebkitMaskSize:'700px 100%',maskRepeat:'no-repeat',WebkitMaskRepeat:'no-repeat',maskPosition:`${bandX-a.x}px 0`,WebkitMaskPosition:`${bandX-a.x}px 0`}}/>}
   </div>
   {label&&<div data-stage10-award-label={a.id} style={{position:'absolute',left:label.x,top:label.y,width:label.width,height:label.height,fontFamily:locale==='en'?'Geist':'Noto Sans TC',fontSize:16,fontWeight:500,lineHeight:'22px',letterSpacing:2,textAlign:'center',whiteSpace:'nowrap',color:palette.paper,opacity:label.opacity,zIndex:0}}>{awardCoupletLabelsStage10[a.id as keyof typeof awardCoupletLabelsStage10][locale]}</div>}
  </React.Fragment>;
 })}</div>;
};
