import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,Audio,Img,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {BackdropStage3} from './ScenesV12Stage3';
import {epicV12Stage5,stage5Timing as timing,stage5Scenes} from '../config/hk-v12-stage5';
import {Stage3Id} from '../config/hk-v12-stage3';
import {OfficialBrandV10} from '../components/OfficialBrandV10';
import {ClosingRevisionR01} from './EndingRevisionR01';
import {AwardsFinal} from '../components/AwardsFinal';
import {GeographicNetworkStage7} from '../components/GeographicNetworkStage7';
import {LogoGridV12} from '../components/LogoGridV12';
import {logoGridV12 as g} from '../config/logo-optical-v12';
import {RingIrisStage5} from '../components/RingIrisStage5';
import captions from '../config/captions-v12-stage3.json';
import offices from '../config/offices-final.json';
import '../fonts';

const C=epicV12Stage5.colors;
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const ease=(v:number)=>1-Math.pow(1-clamp(v),4);
const reveal=(time:number,start=0,d=.6)=>ease((time-start)/d);
const type:React.CSSProperties={fontFamily:'Noto Sans TC',fontWeight:800,letterSpacing:'-.055em',lineHeight:1.12};
const Label:React.FC<{children:React.ReactNode;style?:React.CSSProperties}>=({children,style})=><div style={{position:'absolute',fontFamily:'Noto Sans TC',fontSize:28,fontWeight:500,letterSpacing:6,...style}}>{children}</div>;
const Title:React.FC<{children:React.ReactNode;t:number;size:number;left?:number;top:number;short?:boolean}>=({children,t,size,left=130,top,short=false})=>{
 const p=reveal(t,0,short?.6:.85);return <div style={{position:'absolute',left,top,...type,fontSize:size,opacity:p,transform:`translateY(${(1-p)*(short?18:35)}px)`}}>{children}</div>;
};
const Brand:React.FC<{paper?:boolean}>=({paper=false})=><div style={{position:'absolute',top:66,left:112,width:330,height:92,opacity:paper?.9:.86}}><Img src={staticFile('brand/v10/宏泰.svg')} style={{width:'100%',height:'100%',objectFit:'contain',filter:paper?'none':'brightness(0) invert(1) drop-shadow(0 0 9px rgba(77,177,224,.26))'}}/></div>;
// A single specification applies to every corner label in this composition.
const Meta:React.FC<{children:React.ReactNode}>=({children})=><div data-final-meta style={{position:'absolute',top:94,right:112,fontFamily:'Noto Sans TC',fontSize:20,fontWeight:500,letterSpacing:3,opacity:.65}}>{children}</div>;
const names:Record<Stage3Id,string>={vision:'每一個家族的未來',origin:'時間 · 專業 · 信任',premium:'01 / 集團實力',commission:'02 / 集團實力',clients:'03 / 集團實力',trust:'專業的積累',global:'全球視野 · 一路向前',platform:'家族辦公室平台',office:'三城辦公室 · 公司實景',values:'專業為本 · 穩健為根',roots:'根深 · 步穩 · 向前',close:''};

const DataRings:React.FC<{frame:number}>=({frame})=>{
 const t=(frame-g.premiumStartFrame)/30,commission=frame>=g.commissionStartFrame;
 return <svg width={1920} height={1080} style={{position:'absolute',inset:0}}><g opacity={.24}>{Array.from({length:commission?10:8},(_,i)=>{
  const p=i<8?ease((t-.1-i*.05)/1.8):ease((frame-g.commissionStartFrame)/(30*.5)),r=140+i*115+t*3;
  return <ellipse key={i} cx={960} cy={820} rx={r} ry={r*.53} fill="none" stroke={i>=8?C.paper:i%3===0?C.paper:C.blue} strokeWidth={i>=8?1.4:i%3===0?1.1:.7} opacity={(i>=8?.65:.65-i*.025)*p}/>;
 })}</g></svg>;
};
const Data:React.FC<{frame:number}>=({frame})=>{
 const commission=frame>=g.commissionStartFrame,p=ease((frame-(commission?g.commissionStartFrame:g.premiumStartFrame))/(30*.7));
 const out=commission?1:1-ease((frame-519)/6);
 return <><Brand/><Meta>{commission?names.commission:names.premium}</Meta>
  <Label style={{left:130,top:300}}>集團總{commission?'佣金':'保費'}</Label>
  <div style={{position:'absolute',left:130,top:348,...type,lineHeight:1,letterSpacing:'-.07em',fontSize:commission?300:260,opacity:p*out,transform:`translateY(${(1-p)*18}px)`}}>{commission?'15億+':'100億+'}</div>
  <Label style={{left:130,top:660,fontSize:34,letterSpacing:5}}>港元</Label><LogoGridV12 frame={frame}/>
 </>;
};
const Clients:React.FC<{t:number}>=({t})=>{
 const p=reveal(t,.05,.9);return <><Label style={{left:130,top:245}}>高淨值客戶</Label>
 <div style={{position:'absolute',left:112,top:300,right:112,display:'flex',alignItems:'baseline',gap:30,transform:`translateY(${(1-p)*45}px) scale(${.94+.06*p})`,transformOrigin:'left center',opacity:p}}><span style={{...type,fontSize:330,fontVariantNumeric:'tabular-nums',letterSpacing:'-.07em'}}>2萬+</span></div>
 <Label style={{left:138,top:726,fontSize:34,letterSpacing:5}}>數字背後，是信任。</Label>
 <div style={{position:'absolute',left:135,top:809,width:1450,height:1,background:'linear-gradient(90deg,#2A85A8,transparent)'}}/>
 </>;
};
const Platform:React.FC<{time:number;t:number}>=({time,t})=><>
 <Title t={t} size={116} left={128} top={242}>一個平台，連繫未來。</Title>
 <svg width={1920} height={1080} style={{position:'absolute'}}><path d="M250 740 H1670 M960 740 V510" stroke={C.blue} strokeWidth={2} strokeDasharray={1700} strokeDashoffset={1700*(1-reveal(t,.2,1.6))} fill="none"/>{[250,605,960,1315,1670].map((x,i)=><g key={x} opacity={reveal(t,.4+i*.18,.7)}><circle cx={x} cy={740} r={7} fill={C.paper}/><path d={`M${x} 720 V700`} stroke={C.paper} strokeWidth={1.5}/></g>)}</svg>
 <div style={{position:'absolute',left:710,top:430,width:500,height:160,background:C.paper,padding:22,boxSizing:'border-box',opacity:reveal(t,1,1)}}><Img src={staticFile('brand/v11/evergreen.svg')} style={{width:'100%',height:'100%',objectFit:'contain'}}/></div>
 {['保險','信託','稅務','教育','身份'].map((s,i)=><div key={s} style={{position:'absolute',left:150+i*355,top:770,width:200,textAlign:'center',...type,fontSize:46,letterSpacing:3,opacity:reveal(t,.4+i*.18)}}>{s}</div>)}
 <div data-final-addition="business" style={{position:'absolute',left:150,right:150,top:843,display:'grid',gridTemplateColumns:'1.35fr 1fr 1fr',gap:56,opacity:.72*reveal(time,40.8,.5),fontFamily:'Noto Sans TC',fontSize:26,lineHeight:1.35,letterSpacing:1}}>
  <div>核心保險業務<div style={{fontSize:22,marginTop:7,lineHeight:1.4}}>香港、澳門、美國、百慕達、新加坡保險</div></div><div>家族辦公室</div><div>財富管理</div>
 </div>
</>;
const Office:React.FC<{time:number}>=({time})=>{
 const out=1-ease((time-timing.officeExitStart/30)/.3);
 return <div style={{position:'absolute',inset:0,opacity:out}}>
  <Title t={time-timing.officeContent/30} short size={115} left={125} top={342}>看得全面。<br/>行得長遠。</Title>
  <div style={{position:'absolute',left:132,top:715,width:110,height:4,background:C.blue}}/>
  {offices.map(a=>{const p=reveal(time,a.start,a.entry_seconds),[left,top,width,height]=a.display;return <div key={a.city} data-final-office={a.city} style={{position:'absolute',left,top,width,opacity:p,transform:`translateY(${(1-p)*16}px)`}}>
   <div style={{width,height,overflow:'hidden'}}><Img src={staticFile(a.file)} style={{width:'100%',height:'100%',objectFit:'cover'}}/></div>
   <div style={{marginTop:12,fontFamily:'Noto Sans TC',fontSize:26,fontWeight:500,letterSpacing:3,opacity:.72}}>{a.city}</div>
  </div>;})}
 </div>;
};
const Values:React.FC<{time:number}>=({time})=>{
 const out=1-ease((time-timing.valuesExitStart/30)/((timing.rootsStart-timing.valuesExitStart)/30));
 return <div style={{position:'absolute',inset:0,opacity:out}}>
  <Title short t={time-timing.firstLine/30} size={138} top={330}>眼光，跨越地域。</Title>
  <Title short t={time-timing.secondLine/30} size={143} top={520}>信任，扎根時間。</Title>
  <div style={{position:'absolute',right:150,top:760,fontFamily:'Noto Sans TC',fontSize:24,fontWeight:500,letterSpacing:2,lineHeight:2,opacity:.78*reveal(time,timing.firstLine/30)}}>保監局持牌　FB1681<br/>PIBA會員　M0573</div>
  <div data-final-addition="compliance" style={{position:'absolute',right:150,top:873,width:620,display:'grid',gridTemplateColumns:'1fr 1fr',columnGap:38,rowGap:14,fontFamily:'Noto Sans TC',fontSize:24,fontWeight:500,letterSpacing:1,lineHeight:1.3,opacity:.72*reveal(time,52.12,.4)}}>
   {['全面風險管理','合規操作準則','客戶隱私保護','業務持續運營'].map(s=><div key={s}>{s}</div>)}
  </div>
 </div>;
};
type State={id:Stage3Id;start:number;paper:boolean};
const stateAt=(frame:number):State=>{const s=stage5Scenes.filter(s=>frame>=Math.round(s.start*30)).at(-1)!;return {id:s.id,start:s.start,paper:['office','values','roots','close'].includes(s.id)};};
const Content:React.FC<{state:State;time:number;opacity?:number}>=({state,time,opacity=1})=>{
 const {id,start,paper}=state,t=Math.max(0,time-start);
 return <Sequence from={Math.round(start*30)}><AbsoluteFill style={{opacity,color:paper?C.deep:C.paper}}>
  {id!=='close'&&<><Brand paper={paper}/><Meta>{names[id]}</Meta></>}
  {id==='vision'&&<><div style={{position:'absolute',left:130,top:346}}><div style={{fontFamily:'Noto Sans TC',fontSize:28,fontWeight:500,letterSpacing:6,marginBottom:28,opacity:reveal(t,.6,1.2)}}>未來，值得更長遠的眼光</div><div style={{...type,fontSize:205,opacity:reveal(t-.7,0,.85),transform:`translateY(${(1-reveal(t-.7,0,.85))*35}px)`}}>看得更遠。</div></div><div style={{position:'absolute',left:137,top:700,width:160*reveal(t,3.2,1.2),height:4,background:C.blue}}/></>}
  {id==='origin'&&<><Label style={{left:134,top:252}}>集團源自</Label><div style={{position:'absolute',left:112,top:300,...type,fontSize:360,opacity:reveal(t,0,.85),transform:`translateY(${(1-reveal(t,0,.85))*35}px)`,fontVariantNumeric:'tabular-nums'}}>1997<span style={{color:C.copper,fontSize:100,marginLeft:12}}>年</span></div><Label style={{left:139,top:748,fontSize:31,letterSpacing:3}}>一路走來，承接每一份信任。</Label></>}
  {id==='clients'&&<Clients t={t}/>}
  {id==='trust'&&<><Title t={t} size={88} top={174}>每一份信任，都有分量。</Title><Label style={{left:134,top:280,fontSize:23,letterSpacing:2,opacity:.65}}>業界肯定，見證專業積累</Label><AwardsFinal t={t}/></>}
  {id==='global'&&<><GeographicNetworkStage7 time={time} sceneTime={time-923/30}/><Title t={t} size={96} top={190}>讓眼光，跨越地域。</Title></>}
  {id==='platform'&&<Platform time={time} t={t}/>}
  {id==='office'&&<Office time={time}/>}
  {id==='values'&&<Values time={time}/>}
  {id==='roots'&&<><Title t={t} size={126} left={125} top={340}>根扎得深，<br/>長得更高。</Title><svg width={770} height={695} viewBox="480 390 310 280" style={{position:'absolute',left:1020,top:162}}><OfficialBrandV10 seconds={t*2.4} prefix="epic-tree-v11"/></svg></>}
  {id==='close'&&<ClosingRevisionR01/>}
 </AbsoluteFill></Sequence>;
};
const Background:React.FC<{state:State;time:number}>=({state,time})=><BackdropStage3 t={state.id==='trust'?Math.min(1,time-state.start):Math.max(0,time-state.start)} paper={state.paper} vision={state.id==='vision'}/>;
const Captions:React.FC<{time:number;paper:boolean;watermark:boolean}>=({time,paper,watermark})=>{
 const caption=captions.find(c=>time>=c.start&&time<c.end+.12);
 return <><div data-final-caption style={{position:'absolute',left:105,right:105,bottom:58,textAlign:'center',height:55,fontFamily:'Noto Sans TC',fontWeight:500,fontSize:36,letterSpacing:1,color:paper?C.deep:C.paper,textShadow:paper?'none':'0 2px 12px rgba(0,0,0,.7)',opacity:caption?1:0}}>{caption?.text}</div>
 {watermark&&<div data-final-watermark style={{position:'absolute',left:114,bottom:26,fontFamily:'Noto Sans TC',fontSize:16,letterSpacing:2,color:paper?C.deep:C.paper,opacity:.45}}>內部審片版 · 不作對外發布</div>}</>;
};
export const EpicFilmV12Final:React.FC<{watermark?:boolean;qa?:boolean}>=({watermark=true,qa=false})=>{
 const frame=useCurrentFrame(),time=Math.min(frame/30,68.1),state=stateAt(frame),root=useRef<HTMLDivElement>(null);
 useLayoutEffect(()=>{if(qa&&root.current){const el=root.current,caption=el.querySelector('[data-final-caption]') as HTMLElement|null;
  const metas=Array.from(el.querySelectorAll('[data-final-meta]')).map(m=>{const s=getComputedStyle(m);return {text:m.textContent,top:s.top,right:s.right,fontSize:s.fontSize};});
  console.log('FINAL_AUDIT:'+JSON.stringify({frame,text:el.innerText,caption:caption?.textContent,captionStyle:caption?{bottom:caption.style.bottom,left:caption.style.left,right:caption.style.right,fontSize:caption.style.fontSize,textAlign:caption.style.textAlign}:null,metas,watermark:!!el.querySelector('[data-final-watermark]')}));
 }},[frame,qa,watermark]);
 const iris=frame>=timing.irisStart&&frame<timing.officeContent;
 const data=frame>=g.premiumStartFrame&&frame<g.clientsStartFrame+9;
 const i=stage5Scenes.findIndex(s=>s.id===state.id),s=stage5Scenes[i],prev=stage5Scenes[i-1];
 const sameColor=prev&&!['office','values','roots'].includes(state.id)&&stateAt(Math.round(s.start*30)-1).paper===state.paper;
 const fade=sameColor?clamp((time-s.start)/(state.id==='close'?.4:.3)):1;
 const dataClient=frame>=g.clientsStartFrame,dataFade=clamp((frame-(dataClient?g.clientsStartFrame:g.premiumStartFrame))/9);
 return <AbsoluteFill ref={root} style={{background:'#000'}}><AbsoluteFill style={{opacity:Math.min(1,frame/12)}}>
  {iris?<RingIrisStage5 frame={frame-timing.irisStart} oldScene={<><Background state={stateAt(timing.irisStart)} time={timing.irisStart/30}/><Content state={stateAt(timing.irisStart)} time={timing.irisStart/30}/></>} newBackground={<BackdropStage3 t={0} paper/>}/>:data?<>
   <BackdropStage3 t={dataClient?(frame-g.clientsStartFrame)/30:0}/>{!dataClient&&<DataRings frame={frame}/>}
   {dataClient?<><AbsoluteFill style={{color:C.paper,opacity:1-dataFade}}><Data frame={frame}/></AbsoluteFill><Content state={stateAt(frame)} time={time} opacity={dataFade}/></>:<>
    {dataFade<1&&frame<g.commissionStartFrame&&<Content state={stateAt(g.premiumStartFrame-1)} time={time} opacity={1-dataFade}/>}
    <AbsoluteFill style={{color:C.paper,opacity:dataFade}}><Data frame={frame}/></AbsoluteFill>
   </>}
  </>:<>
   <Background state={state} time={time}/>
   {fade<1&&prev&&<Content state={stateAt(Math.round(s.start*30)-1)} time={time} opacity={1-fade}/>}
   <Content state={state} time={time} opacity={fade}/>
  </>}
  <Captions time={time} paper={iris?frame>=1336:state.paper} watermark={watermark}/>
 </AbsoluteFill><Audio src={staticFile(epicV12Stage5.mix)}/></AbsoluteFill>;
};
