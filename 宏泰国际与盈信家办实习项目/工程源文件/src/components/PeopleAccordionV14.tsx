import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,Img,continueRender,delayRender,staticFile} from 'remotion';
import {peopleLeadsV13,peoplePartnersV13,type PeopleContentV13} from '../config/people-content-v14';
import {getPeopleNarrationV13,type Locale} from '../config/locale-v12';
import {getScreenTextV14 as getScreenTextV12} from '../config/copy-v14';
import {peopleCurveV13,peopleFocusStateV13} from '../config/people-v13';
import '../fonts';
import {fontsReadyV13} from '../fonts-v13';

export type PeopleVisualPlanV13={
 openingFrames:number;
 personFrames:readonly number[];
 returnFrames:number;
 exitFrames:number;
 wallFrames:number;
};
/** Provisional silent visual-study timing, never a claim about final VO length. */
export const peopleVisualStudyPlanV13:PeopleVisualPlanV13={openingFrames:60,personFrames:[72,72,72,72,72,72],returnFrames:15,exitFrames:6,wallFrames:90};
export const peopleVisualDurationV13=(plan:PeopleVisualPlanV13=peopleVisualStudyPlanV13)=>plan.openingFrames+plan.personFrames.reduce((a,b)=>a+b,0)+plan.returnFrames+plan.exitFrames+plan.wallFrames;
type Phase={kind:'opening'|'person'|'return'|'exit'|'wall';index:number;local:number;start:number};
export const peoplePhaseV13=(frame:number,plan:PeopleVisualPlanV13=peopleVisualStudyPlanV13):Phase=>{
 if(plan.personFrames.length!==6||plan.personFrames.some(n=>n<72)||plan.returnFrames<1||plan.exitFrames<1)throw new Error('Invalid people visual plan');
 let start=0;
 if(frame<plan.openingFrames)return {kind:'opening',index:-1,local:Math.max(0,frame),start};
 start=plan.openingFrames;
 for(let index=0;index<6;index++){const count=plan.personFrames[index];if(frame<start+count)return {kind:'person',index,local:frame-start,start};start+=count;}
 if(frame<start+plan.returnFrames)return {kind:'return',index:5,local:frame-start,start};
 start+=plan.returnFrames;
 if(frame<start+plan.exitFrames)return {kind:'exit',index:5,local:frame-start,start};
 start+=plan.exitFrames;return {kind:'wall',index:-1,local:Math.max(0,frame-start),start};
};
const C={paper:'#F4EEE2',warm:'#E9E2D4',ink:'#061C2B',muted:'#41596B',copper:'#B9653F'};
const clamp=(n:number)=>Math.max(0,Math.min(1,n));
const reveal=(frame:number,start:number,duration:number)=>peopleCurveV13((frame-start)/duration);
const font=(locale:Locale)=>locale==='en'?'Geist':'Noto Sans TC';
// The numeric token in Source Serif 4 requires a quoted CSS family name.
const serif=(locale:Locale)=>locale==='en'?'"Source Serif 4"':'"Noto Serif TC"';

/** Manual source-pixel framing references, estimated on the native images.
 * They control composition only, never identify an otherwise unknown face. */
export const peopleEyeFocusV13:Readonly<Record<string,{x:number;y:number;alpha:readonly [number,number,number,number]}>>={
 'david-lau':{x:976,y:474,alpha:[0,0,2015,1657]},
 'patrick-li':{x:395,y:140,alpha:[237,51,584,443]},
 'pamela-cheng':{x:195,y:158,alpha:[68,78,324,371]},
 'manli-chan':{x:363,y:150,alpha:[241,74,509,535]},
 'ken-yeung':{x:351,y:179,alpha:[150,79,573,556]},
 'david-wang':{x:166,y:110,alpha:[3,47,286,382]},
 'lily-ku':{x:216,y:155,alpha:[0,86,430,425]},
 'noah-cheung':{x:136,y:126,alpha:[47,75,277,364]},
 'catherine-luo':{x:165,y:120,alpha:[36,54,280,398]},
 'vivian-mau':{x:145,y:86,alpha:[24,10,273,282]},
 'crystal-wang':{x:208,y:171,alpha:[86,93,362,571]},
};

/** Choose a single native-image scale from the focused window, not from a
 * shrinking card. The shared1.04 motion is accounted for before rendering. */
export const peopleImageGeometryV13=(person:PeopleContentV13,width:number,height:number,motionScale:number,focusWindowWidth=900,peakMotionScale=1.04)=>{
 const eye=peopleEyeFocusV13[person.id],targetY=height/3;
 let required=person.fit==='contain'?Math.min(focusWindowWidth/person.nativeWidth,height/person.nativeHeight):Math.max(focusWindowWidth/person.nativeWidth,height/person.nativeHeight);
 // A covering photo must still cover both sides of its eye anchor.
 if(person.fit==='cover')required=Math.max(required,targetY/eye.y,(height-targetY)/(person.nativeHeight-eye.y),(focusWindowWidth/2)/eye.x,(focusWindowWidth/2)/(person.nativeWidth-eye.x));
 let baseScale=Math.min(required,person.maxScale/peakMotionScale);
 if(person.fit==='contain'){
  // Keep all nontransparent source pixels visible in the focused viewport,
  // while permitting invisible original soft-mask margins outside it.
  const limits=[targetY/(eye.y-eye.alpha[1]),(height-targetY)/(eye.alpha[3]-eye.y),(focusWindowWidth/2)/(eye.x-eye.alpha[0]),(focusWindowWidth/2)/(eye.alpha[2]-eye.x)].filter(n=>n>0);
  baseScale=Math.min(baseScale,...limits.map(n=>n/peakMotionScale));
 }
 const imageWidth=person.nativeWidth*baseScale,imageHeight=person.nativeHeight*baseScale;
 return {baseScale,nativeScale:baseScale*motionScale,width:imageWidth,height:imageHeight,left:width/2-eye.x*baseScale,top:targetY-eye.y*baseScale,eyeX:eye.x,eyeY:eye.y,originX:eye.x*baseScale,originY:eye.y*baseScale};
};

const Photo:React.FC<{person:PeopleContentV13;left:number;top:number;width:number;height:number;focus:number;opacity:number;scale:number;wall?:boolean}>=({person,left,top,width,height,focus,opacity,scale,wall=false})=>{
 const im=peopleImageGeometryV13(person,width,height,scale,wall?300:900,wall?1:1.04),saturation=.55+.35*focus;
 // User revision r04: retain skin tones in every card; focus controls gentle
 // colour strength and opacity on the existing shared width/motion curve.
 return <div data-people-photo={person.id} data-people-photo-kind={wall?'partner':'lead'} data-people-focus={focus} data-people-opacity={opacity} data-people-grayscale={0} data-people-saturation={saturation} data-people-motion-scale={scale} data-people-native-limit={person.maxScale} style={{position:'absolute',left,top,width,height,overflow:'hidden',background:C.warm,opacity}}>
  <Img data-people-image={person.id} data-native-width={person.nativeWidth} data-native-height={person.nativeHeight} data-source-eye-x={im.eyeX} data-source-eye-y={im.eyeY} src={staticFile(person.file)} style={{position:'absolute',left:im.left,top:im.top,width:im.width,height:im.height,maxWidth:'none',filter:`contrast(1.04) saturate(${saturation}) brightness(1)`,transform:`scale(${scale})`,transformOrigin:`${im.originX}px ${im.originY}px`}}/>
 </div>;
};

const TextBand:React.FC<{person:PeopleContentV13;locale:Locale;left:number;opacity:number;offset:number;local:number;outgoing?:boolean}>=({person,locale,left,opacity,offset,local,outgoing=false})=>{
 const width=Math.min(900,1790-left),base:React.CSSProperties={position:'absolute',left:0,width,fontFamily:font(locale),fontWeight:500,color:C.ink};
 const progress=(delay:number)=>outgoing?1:reveal(local,9.6+delay,9);
 return <div data-people-band={person.id} data-people-outgoing={outgoing} style={{position:'absolute',left,top:850,width,height:158,opacity}}>
  <div data-people-text="name" data-people-owner={person.id} data-people-fit="single" data-people-base-size={44} data-people-min-size={36} style={{...base,top:0,fontFamily:serif(locale),fontSize:44,lineHeight:'52px',whiteSpace:'nowrap',opacity:progress(0),transform:`translateY(${offset+12*(1-progress(0))}px)`}}>{person.name[locale]}</div>
  <div data-people-text="role" data-people-owner={person.id} data-people-fit="single" data-people-base-size={20} data-people-min-size={18} style={{...base,top:62,color:C.copper,fontSize:20,lineHeight:'28px',whiteSpace:'nowrap',opacity:progress(2.4),transform:`translateY(${offset+12*(1-progress(2.4))}px)`}}>{person.role[locale]}</div>
  <div data-people-text="merits" data-people-owner={person.id} data-people-fit="two-lines" data-people-base-size={20} data-people-min-size={18} style={{...base,top:100,color:C.muted,fontSize:20,lineHeight:'26px',whiteSpace:'normal',overflowWrap:'normal',opacity:progress(4.8),transform:`translateY(${offset+12*(1-progress(4.8))}px)`}}>{person.merits[locale].join(' · ')}</div>
 </div>;
};
const captionId=(phase:Phase)=>phase.kind==='opening'?'opening':phase.kind==='wall'?'partner-wall':phase.index===0?'david-lau':phase.index===1?'patrick-li':phase.index<=3?'operations-compliance':'hong-kong-new-york';

export const PeopleAccordionV14:React.FC<{frame:number;locale?:Locale;plan?:PeopleVisualPlanV13;qa?:boolean;watermark?:boolean;captionText?:string|null}>=({frame,captionText,locale='yue',plan=peopleVisualStudyPlanV13,qa=false,watermark=true})=>{
 const total=peopleVisualDurationV13(plan),safeFrame=Math.min(total-1,Math.max(0,frame)),phase=peoplePhaseV13(safeFrame,plan),root=useRef<HTMLDivElement>(null);
 const focus=phase.kind==='person'?peopleFocusStateV13(phase.index===0?null:phase.index-1,phase.index,phase.local):phase.kind==='return'?peopleFocusStateV13(5,null,6+15*phase.local/plan.returnFrames):peopleFocusStateV13(null,null,21);
 const rowOpacity=phase.kind==='opening'?reveal(phase.local,0,12):phase.kind==='exit'?1-reveal(phase.local,0,plan.exitFrames):phase.kind==='wall'?0:1;
 const rowOffset=phase.kind==='exit'?-24*reveal(phase.local,0,plan.exitFrames):0;
 const current=phase.kind==='person'?peopleLeadsV13[phase.index]:null;
 const old=phase.kind==='person'&&phase.index>0?peopleLeadsV13[phase.index-1]:phase.kind==='return'||phase.kind==='exit'?peopleLeadsV13[5]:null;
 const oldFade=phase.kind==='person'?1-reveal(phase.local,0,6):phase.kind==='return'?1-reveal(phase.local,0,6):0;
 const titleProgress=reveal(safeFrame,0,12);
 const caption=captionText===undefined?getPeopleNarrationV13(locale,captionId(phase)):captionText;

 useLayoutEffect(()=>{
  const handle=delayRender('People V13 font fit and browser geometry');let cancelled=false,done=false,raf1=0,raf2=0;
  const finish=()=>{if(!done){done=true;continueRender(handle);}};
  const fitAndMeasure=()=>{
   if(cancelled||!root.current){finish();return;}
   const el=root.current;
   for(const element of Array.from(el.querySelectorAll<HTMLElement>('[data-people-fit]'))){
    const base=Number(element.dataset.peopleBaseSize),min=Number(element.dataset.peopleMinSize);element.style.fontSize=`${base}px`;
    const two=element.dataset.peopleFit==='two-lines',maxHeight=two?52:Infinity;
    for(let size=base;size>=min;size--){element.style.fontSize=`${size}px`;if((two?element.scrollHeight<=maxHeight:element.scrollWidth<=element.clientWidth))break;}
   }
   raf2=requestAnimationFrame(()=>{
    if(cancelled||!root.current){finish();return;}
    if(qa){
     const r=el.getBoundingClientRect(),scale=r.width/1920;
     const rect=(e:Element)=>{const b=e.getBoundingClientRect();return {x:(b.x-r.x)/scale,y:(b.y-r.y)/scale,width:b.width/scale,height:b.height/scale};};
     const ink=(e:Element)=>{const range=document.createRange();range.selectNodeContents(e);const b=range.getBoundingClientRect();return {x:(b.x-r.x)/scale,y:(b.y-r.y)/scale,width:b.width/scale,height:b.height/scale};};
     const effectiveOpacity=(e:Element)=>{let opacity=1,node:Element|null=e;while(node&&node!==el){opacity*=Number(getComputedStyle(node).opacity);node=node.parentElement;}return opacity;};
     // Range rectangles contain font ascender/descender reserves. Canvas ink
     // metrics on each actual DOM-wrapped line separately report glyph bounds.
     const glyphs=(e:HTMLElement)=>{
      const style=getComputedStyle(e),canvas=document.createElement('canvas'),ctx=canvas.getContext('2d')!;
      ctx.font=`${style.fontStyle} ${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;
      const groups:{y:number;x:number;text:string}[]=[],walker=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let node:Node|null;
      while((node=walker.nextNode()))for(let i=0;i<(node.textContent?.length??0);i++){
       const rg=document.createRange();rg.setStart(node,i);rg.setEnd(node,i+1);const b=rg.getBoundingClientRect();
       if(!b.width&&!b.height)continue;
       let line=groups.find(a=>Math.abs(a.y-b.y)<.5);if(!line){line={y:b.y,x:b.x,text:''};groups.push(line);}line.x=Math.min(line.x,b.x);line.text+=node.textContent![i];
      }
      const lines=groups.map(line=>{const m=ctx.measureText(line.text),ascent=m.fontBoundingBoxAscent??Number.parseFloat(style.fontSize);return {text:line.text,x:(line.x-m.actualBoundingBoxLeft-r.x)/scale,y:(line.y+ascent-m.actualBoundingBoxAscent-r.y)/scale,width:(m.actualBoundingBoxLeft+m.actualBoundingBoxRight)/scale,height:(m.actualBoundingBoxAscent+m.actualBoundingBoxDescent)/scale};});
      if(!lines.length)return {lines,rect:null};
      const x=Math.min(...lines.map(l=>l.x)),y=Math.min(...lines.map(l=>l.y));return {lines,rect:{x,y,width:Math.max(...lines.map(l=>l.x+l.width))-x,height:Math.max(...lines.map(l=>l.y+l.height))-y}};
     };
     const photos=Array.from(el.querySelectorAll<HTMLElement>('[data-people-photo]')).map(e=>{
      const image=e.querySelector<HTMLImageElement>('[data-people-image]')!,raw=rect(image),nativeWidth=Number(image.dataset.nativeWidth),nativeHeight=Number(image.dataset.nativeHeight);
      const card=rect(e),sourceEyeX=Number(image.dataset.sourceEyeX),sourceEyeY=Number(image.dataset.sourceEyeY),nativeScaleX=raw.width/nativeWidth,nativeScaleY=raw.height/nativeHeight;
      return {id:e.dataset.peoplePhoto,kind:e.dataset.peoplePhotoKind,rect:card,rawImage:raw,nativeWidth,nativeHeight,nativeScaleX,nativeScaleY,sourceEye:{x:sourceEyeX,y:sourceEyeY},screenEye:{x:raw.x+sourceEyeX*nativeScaleX,y:raw.y+sourceEyeY*nativeScaleY},targetEye:{x:card.x+card.width/2,y:card.y+card.height/3},limit:Number(e.dataset.peopleNativeLimit),focus:Number(e.dataset.peopleFocus),grayscale:Number(e.dataset.peopleGrayscale),saturation:Number(e.dataset.peopleSaturation),computedImageFilter:getComputedStyle(image).filter,computedCardOpacity:Number(getComputedStyle(e).opacity),declaredOpacity:Number(e.dataset.peopleOpacity),opacity:effectiveOpacity(e),motionScale:Number(e.dataset.peopleMotionScale),clip:getComputedStyle(e).overflow};
     });
     const texts=Array.from(el.querySelectorAll<HTMLElement>('[data-people-text]')).map(e=>{const s=getComputedStyle(e),glyph=glyphs(e);return {role:e.dataset.peopleText,owner:e.dataset.peopleOwner??null,text:e.textContent,rect:rect(e),fontRect:ink(e),glyphRect:glyph.rect,glyphLines:glyph.lines,opacity:effectiveOpacity(e),fontSize:s.fontSize,fontFamily:s.fontFamily,lineHeight:s.lineHeight,scrollWidth:e.scrollWidth,clientWidth:e.clientWidth,scrollHeight:e.scrollHeight};});
     console.log('PEOPLE_V13_AUDIT:'+JSON.stringify({frame:safeFrame,locale,phase:phase.kind,index:phase.index,local:phase.local,visualStudy:plan===peopleVisualStudyPlanV13&&captionText===undefined,captionMode:captionText===undefined?'phase-study':'audio-cue',totalFrames:total,root:{width:r.width,height:r.height},photoTotalWidth:focus.totalWidth,photoRight:focus.right,progress:focus.progress,photos,texts}));
    }
    finish();
   });
  };
  fontsReadyV13.then(()=>document.fonts.ready).then(()=>{if(cancelled){finish();return;}raf1=requestAnimationFrame(fitAndMeasure);}).catch(finish);
  return()=>{cancelled=true;cancelAnimationFrame(raf1);cancelAnimationFrame(raf2);finish();};
 },[safeFrame,locale,qa,watermark,total,captionText]);

 return <AbsoluteFill ref={root} data-people-root style={{width:1920,height:1080,background:C.paper,color:C.ink,fontFamily:font(locale),overflow:'hidden'}}>
  <div data-people-text="title" style={{position:'absolute',left:130,top:120,width:1660,fontSize:48,fontWeight:700,lineHeight:'62px',opacity:titleProgress}}>{getScreenTextV12(locale,'peopleTitle')}</div>
  {phase.kind!=='wall'&&<div data-people-row style={{position:'absolute',inset:0,opacity:rowOpacity,transform:`translateY(${rowOffset}px)`}}>
   {focus.items.map(s=><Photo key={s.index} person={peopleLeadsV13[s.index]} left={s.left} top={260} width={s.width} height={570} focus={s.focus} opacity={.65+.35*s.focus} scale={s.scale}/>)}
  </div>}
  {old&&oldFade>0&&<TextBand person={old} locale={locale} left={phase.kind==='person'?focus.items[phase.index-1].left:890} opacity={oldFade} offset={-12*(1-oldFade)} local={phase.local} outgoing/>}
  {current&&<TextBand person={current} locale={locale} left={focus.items[phase.index].left} opacity={1} offset={0} local={phase.local}/>}
  {phase.kind==='wall'&&peoplePartnersV13.map((person,index)=>{
   const p=reveal(phase.local,index*3,9),left=130+index*340,offset=24*(1-p);
   return <div key={person.id} data-people-partner={person.id} style={{position:'absolute',left,top:320+offset,width:300,height:480,opacity:p}}>
    <Photo person={person} left={0} top={0} width={300} height={400} focus={1} opacity={1} scale={1} wall/>
    <div data-people-text="partner-name" data-people-owner={person.id} style={{position:'absolute',left:0,top:416,width:300,fontFamily:font(locale),fontSize:18,fontWeight:500,lineHeight:'28px',textAlign:'center',whiteSpace:'nowrap'}}>{person.name[locale]}</div>
    <div data-people-text="partner-role" data-people-owner={person.id} style={{position:'absolute',left:0,top:449,width:300,fontFamily:font(locale),fontSize:14,lineHeight:'22px',textAlign:'center'}}>{person.role[locale]}</div>
   </div>;
  })}
  <div data-people-text="caption" data-people-fit="single" data-people-base-size={36} data-people-min-size={32} style={{position:'absolute',left:105,top:1018,width:1710,height:48,fontFamily:font(locale),fontSize:36,fontWeight:500,lineHeight:'48px',textAlign:'center',whiteSpace:'nowrap'}}>{caption}</div>
  {watermark&&<div data-people-text="watermark" style={{position:'absolute',left:114,bottom:8,fontFamily:font(locale),fontSize:10,fontWeight:400,lineHeight:'14px',opacity:.28,whiteSpace:'nowrap'}}>{getScreenTextV12(locale,'watermark')}</div>}
 </AbsoluteFill>;
};
