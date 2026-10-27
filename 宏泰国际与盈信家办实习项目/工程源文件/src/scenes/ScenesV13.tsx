import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,continueRender,delayRender} from 'remotion';
import {stage5Scenes} from '../config/hk-v12-stage5';
import type {Stage3Id} from '../config/hk-v12-stage3';
import {logoGridV12 as g} from '../config/logo-optical-v12';
import {officesV12} from '../config/offices-v12';
import {getCaptionAtV12,getScreenTextV12,type Locale} from '../config/locale-v12';
import {getNumericScreenValuesV13,getScreenCopyV13,type TextScreenCopyIdV13} from '../config/screen-copy-v13';
import {themeV13 as C,clampV13 as clamp,easeV13 as ease,revealV13 as reveal} from '../config/theme-v13';
import {BackdropV13} from '../components/BackdropV13';
import {BrandV13,MetaV13,FooterV13,TextV13} from '../components/FilmChromeV13';
import {LogoGridV13} from '../components/LogoGridV13';
import {AwardsStage10} from '../components/AwardsStage10';
import {GeographicNetworkV13,type RouteTimingV13} from '../components/GeographicNetworkV13';
export type MapClockV13={time:number;sceneTime:number;timing:RouteTimingV13};
import {PlatformV13} from '../components/PlatformV13';
import {OfficesV13} from '../components/OfficesV13';
import {ClosingV13} from '../components/ClosingV13';
import {OfficialBrandV10} from '../components/OfficialBrandV10';
import {RingIrisStage5} from '../components/RingIrisStage5';
import {PeopleAccordionV13,peopleVisualDurationV13,type PeopleVisualPlanV13} from '../components/PeopleAccordionV13';
import {fontsReadyV13} from '../fonts-v13';

export const filmBaseFramesV13=2103;
export const peopleInsertionFrameV13=1652;
type State={id:Stage3Id;start:number;paper:boolean};
const stateAt=(f:number):State=>{const s=stage5Scenes.filter(s=>f>=Math.round(s.start*30)).at(-1)!;return {id:s.id,start:s.start,paper:['office','values','roots','close'].includes(s.id)};};
const metaKeys:Partial<Record<Stage3Id,TextScreenCopyIdV13>>={vision:'meta.vision',origin:'meta.origin',premium:'meta.premium',commission:'meta.commission',clients:'meta.clients',trust:'meta.awards',global:'meta.map',platform:'meta.platform',office:'meta.offices',roots:'meta.roots'};
const Title:React.FC<{id:string;locale:Locale;time:number;children:React.ReactNode;size:number;left?:number;top:number;width?:number;lines?:number}>=({id,locale,time,children,size,left=130,top,width=1660,lines=1})=>{const p=reveal(time);return <TextV13 id={id} locale={locale} size={size} minSize={Math.min(58,size*.55)} lines={lines} style={{left,top,width,fontWeight:800,lineHeight:1.12,letterSpacing:'-.055em',opacity:p,transform:`translateY(${35*(1-p)}px)`}}>{children}</TextV13>;};

const DataRings:React.FC<{sourceFrame:number}>=({sourceFrame:f})=>{const t=(f-g.premiumStartFrame)/30,commission=f>=g.commissionStartFrame;return <svg width={1920} height={1080} style={{position:'absolute',inset:0}}><g opacity={.06}>{Array.from({length:commission?10:8},(_,i)=>{const p=i<8?ease((t-.1-i*.05)/1.8):ease((f-g.commissionStartFrame)/15),r=140+i*115+t*3;return <ellipse key={i} cx={960} cy={820} rx={r} ry={r*.53} fill="none" stroke={i>=8?C.paper:i%3===0?C.paper:C.blue} strokeWidth={i>=8?1.4:i%3===0?1.1:.7} opacity={(i>=8?.65:.65-i*.025)*p}/>;})}</g></svg>;};

const Data:React.FC<{sourceFrame:number;locale:Locale}>=({sourceFrame:f,locale})=>{
 const commission=f>=g.commissionStartFrame,p=ease((f-(commission?g.commissionStartFrame:g.premiumStartFrame))/21),out=commission?1:1-ease((f-519)/6),values=getNumericScreenValuesV13(locale);
 return <><BrandV13/><MetaV13 locale={locale} text={getScreenCopyV13(locale,commission?'meta.commission':'meta.premium')}/>
  <TextV13 id={commission?'commission.label':'premium.label'} locale={locale} size={28} minSize={22} style={{left:130,top:300,width:commission?730:820,letterSpacing:locale==='en'?1:6}}>{getScreenCopyV13(locale,commission?'commission.label':'premium.label')}</TextV13>
  <TextV13 id="data.value" locale={locale} size={commission?300:260} minSize={100} style={{left:130,top:348,width:commission?740:830,fontWeight:800,lineHeight:1,letterSpacing:'-.07em',opacity:p*out,transform:`translateY(${18*(1-p)}px)`}}>{commission?values.commission:values.premium}</TextV13>
  <TextV13 id="data.currency" locale={locale} size={34} minSize={24} style={{left:130,top:660,width:730,letterSpacing:locale==='en'?1:5}}>{getScreenCopyV13(locale,'data.currency')}</TextV13><LogoGridV13 sourceFrame={f} locale={locale}/>
 </>;
};

const GenericContent:React.FC<{state:State;sourceFrame:number;locale:Locale;opacity?:number}>=({state,sourceFrame:f,locale,opacity=1})=>{
 const {id,start,paper}=state,t=Math.max(0,f/30-start),copy=(key:TextScreenCopyIdV13)=>getScreenCopyV13(locale,key);
 const year=copy('origin.year'),clientP=reveal(t,.05,.9);
 return <AbsoluteFill style={{opacity,color:paper?C.ink:C.paper}}>
  {id!=='close'&&<><BrandV13 paper={paper}/><MetaV13 locale={locale} paper={paper} text={metaKeys[id]?copy(metaKeys[id]!):getScreenTextV12(locale,'valuesMeta')}/></>}
  {id==='vision'&&<><div style={{position:'absolute',left:130,top:346}}><TextV13 id="vision.subtitle" locale={locale} size={28} minSize={22} style={{position:'relative',width:1660,letterSpacing:locale==='en'?1:6,marginBottom:28,opacity:reveal(t,.6,1.2)}}>{getScreenTextV12(locale,'visionSubtitle')}</TextV13><TextV13 id="vision.title" locale={locale} size={205} minSize={100} style={{position:'relative',width:1660,fontWeight:800,lineHeight:1.12,letterSpacing:'-.055em',opacity:reveal(t-.7),transform:`translateY(${35*(1-reveal(t-.7))}px)`}}>{getScreenTextV12(locale,'visionTitle')}</TextV13></div><div style={{position:'absolute',left:137,top:700,width:160*reveal(t,3.2,1.2),height:4,background:C.blue}}/></>}
  {id==='origin'&&<><TextV13 id="origin.label" locale={locale} size={28} minSize={22} style={{left:134,top:252,width:1660,letterSpacing:locale==='en'?1:6}}>{copy('origin.label')}</TextV13><TextV13 id="origin.year" locale={locale} size={360} minSize={200} style={{left:112,top:300,width:1660,fontWeight:800,lineHeight:1.12,letterSpacing:'-.055em',opacity:reveal(t),transform:`translateY(${35*(1-reveal(t))}px)`,fontVariantNumeric:'tabular-nums'}}>1997<span style={{color:C.copper,fontSize:100,marginLeft:12}}>{year.slice(4)}</span></TextV13><TextV13 id="origin.support" locale={locale} size={31} minSize={24} style={{left:139,top:748,width:1600,letterSpacing:locale==='en'?1:3}}>{copy('origin.support')}</TextV13></>}
  {id==='clients'&&<><TextV13 id="clients.label" locale={locale} size={28} minSize={22} style={{left:130,top:245,width:1660,letterSpacing:locale==='en'?1:6}}>{copy('clients.label')}</TextV13><TextV13 id="clients.value" locale={locale} size={330} minSize={180} style={{left:112,top:300,width:1696,fontWeight:800,lineHeight:1.12,letterSpacing:'-.07em',fontVariantNumeric:'tabular-nums',opacity:clientP,transform:`translateY(${45*(1-clientP)}px) scale(${.94+.06*clientP})`,transformOrigin:'left center'}}>{getNumericScreenValuesV13(locale).clients}</TextV13><TextV13 id="clients.support" locale={locale} size={34} minSize={25} style={{left:138,top:726,width:1600,letterSpacing:locale==='en'?1:5}}>{copy('clients.support')}</TextV13><div style={{position:'absolute',left:135,top:809,width:1450,height:1,background:`linear-gradient(90deg,${C.blue},transparent)`}}/></>}
  {id==='roots'&&<><Title id="roots.title" locale={locale} time={t} size={126} left={125} top={340} width={885} lines={2}>{copy('roots.title')}</Title><svg width={770} height={695} viewBox="480 390 310 280" style={{position:'absolute',left:1020,top:162}}><OfficialBrandV10 seconds={t*2.4} prefix="roots-v13"/></svg></>}
  {id==='close'&&<ClosingV13 sceneFrame={f-Math.round(start*30)} locale={locale}/>}
 </AbsoluteFill>;
};

const PlatformSnapshot:React.FC<{locale:Locale}>=({locale})=><AbsoluteFill style={{color:C.paper}}><BackdropV13 time={2.8}/><PlatformV13 sceneTime={(1323-1141)/30} locale={locale}/><BrandV13/><MetaV13 locale={locale} text={getScreenCopyV13(locale,'meta.platform')}/></AbsoluteFill>;

const BasePicture:React.FC<{sourceFrame:number;locale:Locale;mapClock?:MapClockV13}>=({sourceFrame:f,locale,mapClock})=>{
 const state=stateAt(f),t=f/30-state.start;
 if(f>=705&&f<1359){
  const phase=f<864?'awards':f<1141?'map':f<1323?'platform':'iris';
  if(phase==='iris')return <RingIrisStage5 frame={f-1323} oldScene={<PlatformSnapshot locale={locale}/>} newBackground={<BackdropV13 time={0} paper/>}/>;
  return <><BackdropV13 time={phase==='awards'?Math.min(1,(f-705)/30):phase==='map'?4:Math.min(2.8,(f-1141)/30)}/><BrandV13/>
   {phase==='awards'?<><MetaV13 locale={locale} text={getScreenCopyV13(locale,'meta.awards')}/><Title id="awards.title" locale={locale} time={(f-705)/30} top={174} size={88}>{getScreenTextV12(locale,'awardsTitle')}</Title><TextV13 id="awards.subtitle" locale={locale} size={23} minSize={20} style={{left:134,top:280,width:1660,letterSpacing:2,opacity:1}}>{getScreenTextV12(locale,'awardsSubtitle')}</TextV13><AwardsStage10 sceneTime={(f-705)/30} locale={locale} colors={C}/></>:phase==='map'?<><div className="v13-geographic"><GeographicNetworkV13 time={mapClock?.time??f/30} sceneTime={mapClock?.sceneTime??(f-864)/30} customTiming={mapClock?.timing} locale={locale} landFill={C.land} landStroke={C.landStroke}/></div><MetaV13 locale={locale} text={getScreenCopyV13(locale,'meta.map')}/><Title id="map.title" locale={locale} time={(f-864)/30} top={190} size={96}>{getScreenCopyV13(locale,'map.title')}</Title></>:<><PlatformV13 sceneTime={(f-1141)/30} locale={locale}/><MetaV13 locale={locale} text={getScreenCopyV13(locale,'meta.platform')}/></>}
  </>;
 }
 if(f>=1359&&f<1652){const trust=f>=officesV12.trustStart;return <><BackdropV13 time={0} paper/><BrandV13 paper/><MetaV13 locale={locale} paper text={trust?getScreenTextV12(locale,'valuesMeta'):getScreenCopyV13(locale,'meta.offices')}/><OfficesV13 sourceFrame={f} locale={locale}/></>;}
 const data=f>=431&&f<618;
 if(data){const clients=f>=609,fade=clamp((f-(clients?609:431))/9);return <><BackdropV13 time={clients?(f-609)/30:0}/>{!clients&&<DataRings sourceFrame={f}/>}{clients?<><AbsoluteFill style={{opacity:1-fade,color:C.paper}}><Data sourceFrame={f} locale={locale}/></AbsoluteFill><GenericContent state={state} sourceFrame={f} locale={locale} opacity={fade}/></>:<>{fade<1&&f<525&&<GenericContent state={stateAt(430)} sourceFrame={f} locale={locale} opacity={1-fade}/>}<AbsoluteFill style={{opacity:fade,color:C.paper}}><Data sourceFrame={f} locale={locale}/></AbsoluteFill></>}</>;}
 const index=stage5Scenes.findIndex(s=>s.id===state.id),prev=stage5Scenes[index-1],same=prev&&!['office','values','roots'].includes(state.id)&&stateAt(Math.round(state.start*30)-1).paper===state.paper,fade=same?clamp(t/(state.id==='close'?.4:.3)):1;
 return <><BackdropV13 time={Math.max(0,t)} paper={state.paper} vision={state.id==='vision'}/>{fade<1&&prev&&<GenericContent state={stateAt(Math.round(state.start*30)-1)} sourceFrame={f} locale={locale} opacity={1-fade}/>}<GenericContent state={state} sourceFrame={f} locale={locale} opacity={fade}/></>;
};

/** QA is a real browser/font layout pass, not a character-count estimate. It
 * reports each visible UI text node, fill/opacity/background and safe bounds. */
export const usePictureAuditV13=(root:React.RefObject<HTMLDivElement|null>,sourceFrame:number,locale:Locale,qa:boolean)=>{
 useLayoutEffect(()=>{const handle=delayRender('V13 complete screen-copy font fit');let cancelled=false,done=false,raf1=0,raf2=0;const finish=()=>{if(!done){done=true;continueRender(handle);}};
  fontsReadyV13.then(()=>document.fonts.ready).then(()=>{if(cancelled){finish();return;}raf1=requestAnimationFrame(()=>{
   const el=root.current;if(!el){finish();return;}
   for(const e of Array.from(el.querySelectorAll<HTMLElement>('[data-v13-fit]'))){const base=Number(e.dataset.v13BaseSize),min=Number(e.dataset.v13MinSize),lines=Number(e.dataset.v13Lines);for(let size=base;size>=min;size--){e.style.fontSize=`${size}px`;const s=getComputedStyle(e),lineHeight=parseFloat(s.lineHeight);if(e.scrollWidth<=e.clientWidth+1&&(lines===1||e.scrollHeight<=lineHeight*lines+1))break;}}
   raf2=requestAnimationFrame(()=>{if(cancelled||!root.current){finish();return;}if(qa){const r=el.getBoundingClientRect(),scale=r.width/1920;const box=(e:Element)=>{const b=e.getBoundingClientRect();return {x:(b.x-r.x)/scale,y:(b.y-r.y)/scale,width:b.width/scale,height:b.height/scale};};const opacity=(e:Element)=>{let n:Element|null=e,v=1;while(n){v*=Number(getComputedStyle(n).opacity);if(n===el)break;n=n.parentElement;}return v;};
    const designText=Array.from(el.querySelectorAll('[data-v13-text], [data-stage10-award-label], svg text, [data-v13-text-asset]')).map((e,i)=>{const style=getComputedStyle(e),range=document.createRange();range.selectNodeContents(e);const rr=range.getBoundingClientRect(),b=box(e);return {id:e.getAttribute('data-v13-text')??e.getAttribute('data-stage10-award-label')??e.getAttribute('data-v13-text-asset')??`map.svg.${i}`,text:e.getAttribute('data-v13-text-value')??e.textContent,rect:b,fontRect:{x:(rr.x-r.x)/scale,y:(rr.y-r.y)/scale,width:rr.width/scale,height:rr.height/scale},opacity:opacity(e),fontSize:style.fontSize,fontFamily:style.fontFamily,lineHeight:style.lineHeight,color:style.color,fill:style.fill,stroke:style.stroke,backgroundColor:style.backgroundColor,textShadow:style.textShadow,clip:style.overflow,scrollWidth:e instanceof HTMLElement?e.scrollWidth:null,clientWidth:e instanceof HTMLElement?e.clientWidth:null};}).filter(e=>e.opacity>0&&e.rect.width>0&&e.rect.height>0);
    console.log('FILM_V13_AUDIT:'+JSON.stringify({sourceFrame,locale,pictureOnly:true,theme:C,root:{width:r.width,height:r.height},designText,assetExceptions:Array.from(el.querySelectorAll('[data-v13-asset-language-exception]')).map(e=>({kind:e.getAttribute('data-v13-asset-language-exception'),rect:box(e)}))}));
   }finish();});
  });}).catch(finish);return()=>{cancelled=true;cancelAnimationFrame(raf1);cancelAnimationFrame(raf2);finish();};
 },[sourceFrame,locale,qa]);
};

export type FilmPicturePropsV13={sourceFrame:number;locale?:Locale;watermark?:boolean;qa?:boolean;captionText?:string|null;mapClock?:MapClockV13};
/** Base2103-frame shared picture. Explicit sourceFrame preserves old suffix
 * timing when its displayed position is shifted by an inserted segment. */
export const FilmPictureV13:React.FC<FilmPicturePropsV13>=({sourceFrame,locale='yue',watermark=true,qa=false,captionText,mapClock})=>{
 const f=Math.min(2102,Math.max(0,sourceFrame)),root=useRef<HTMLDivElement>(null),state=stateAt(f),paper=f>=1359||(f>=1336&&f<1359),trust=f>=1569&&f<1652;
 usePictureAuditV13(root,f,locale,qa);
 const caption=captionText===undefined?getCaptionAtV12(locale,Math.min(f/30,68.1))?.text??null:captionText;
 const legal=trust?[getScreenCopyV13(locale,'legal.licences'),getScreenCopyV13(locale,'legal.compliance')]:undefined;
 return <AbsoluteFill ref={root} data-v13-root style={{width:1920,height:1080,background:C.deep,color:paper?C.ink:C.paper,overflow:'hidden'}}>
  <style>{`.v13-geographic svg text {paint-order:stroke;stroke:${C.deep};stroke-width:3px;stroke-linejoin:round;}`}</style>
  <AbsoluteFill style={{opacity:Math.min(1,f/12)}}><BasePicture sourceFrame={f} locale={locale} mapClock={mapClock}/><FooterV13 locale={locale} caption={caption} paper={paper||state.paper} watermark={watermark} legal={legal} legalProgress={trust?ease((f-1569)/11):1}/></AbsoluteFill>
 </AbsoluteFill>;
};

export type FilmWithPeoplePropsV13=Omit<FilmPicturePropsV13,'sourceFrame'> & {frame:number;peoplePlan?:PeopleVisualPlanV13;insertBeforeOriginalFrame?:number};
export const filmWithPeopleDurationV13=(peoplePlan?:PeopleVisualPlanV13)=>filmBaseFramesV13+(peoplePlan?peopleVisualDurationV13(peoplePlan):0);
/** No plan means the70.1s localized base. A caller supplies measured final
 * people timings; the default603f silent study is never silently selected. */
export const FilmWithPeoplePictureV13:React.FC<FilmWithPeoplePropsV13>=({frame,peoplePlan,insertBeforeOriginalFrame=peopleInsertionFrameV13,...props})=>{
 const delta=peoplePlan?peopleVisualDurationV13(peoplePlan):0;
 if(peoplePlan&&frame>=insertBeforeOriginalFrame&&frame<insertBeforeOriginalFrame+delta)return <PeopleAccordionV13 frame={frame-insertBeforeOriginalFrame} locale={props.locale} plan={peoplePlan} qa={props.qa} watermark={props.watermark} captionText={props.captionText}/>;
 return <FilmPictureV13 {...props} sourceFrame={frame>=insertBeforeOriginalFrame+delta?frame-delta:frame}/>;
};
