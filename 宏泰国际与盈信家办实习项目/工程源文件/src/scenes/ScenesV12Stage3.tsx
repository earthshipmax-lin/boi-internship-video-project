import React from 'react';
import {AbsoluteFill,Audio,Img,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {OfficialBrandV10} from '../components/OfficialBrandV10';
import {epicV12Stage3,stage3Scenes,paperAtStage3,Stage3Id,sourceTimeStage3} from '../config/hk-v12-stage3';
type TransitionType='cut'|'crossfade';
import {AwardsStage3} from '../components/AwardsStage3';
import logoSpec from '../config/logos-stage2.json';
import {PhotoBand,photoEase} from '../components/PhotoBand';
import {GeographicNetworkV12} from '../components/GeographicNetworkV12';
import {providerLogos,bankLogos,awardPhotos} from '../config/photos-v12';
import {ClosingRevisionR01} from './EndingRevisionR01';
import beats from '../config/beats-v11.json';
import captions from '../config/captions-v12-stage3.json';
import '../fonts';
const C=epicV12Stage3.colors;
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
const ease=(x:number)=>1-Math.pow(1-clamp(x),4);
const reveal=(t:number,start=0,dur=.85)=>ease((t-start)/dur);
const textStyle:React.CSSProperties={fontFamily:'"Noto Sans TC",sans-serif',fontWeight:800,letterSpacing:'-.055em',lineHeight:1.12};
const Label:React.FC<{children:React.ReactNode;light?:boolean;style?:React.CSSProperties}>=({children,light=false,style})=><div style={{fontFamily:'"Noto Sans TC"',fontSize:28,fontWeight:500,letterSpacing:6,color:light?C.deep:C.paper,...style}}>{children}</div>;
const Title:React.FC<{children:React.ReactNode;t:number;size?:number;style?:React.CSSProperties}>=({children,t,size=150,style})=>{const p=reveal(t);return <div style={{...textStyle,fontSize:size,opacity:p,transform:`translateY(${(1-p)*35}px)`,...style}}>{children}</div>;};
const Rings:React.FC<{t:number;vision?:boolean;extra?:number}>=({t,vision=false,extra=0})=>{const growth=vision?Math.max(0,t-3.2)*1.5:Math.min(t,66)*3;return <svg width={1920} height={1080} style={{position:'absolute',inset:0}}><g opacity={.24}>{Array.from({length:12+extra},(_,i)=><ellipse key={i} cx={960} cy={820} rx={140+i*115+growth} ry={(140+i*115+growth)*.53} fill="none" stroke={i>=12?C.paper:i%3===0?C.paper:C.blue} strokeWidth={i>=12?1.4:i%3===0?1.1:.7} opacity={(i>=12?.82:.65-i*.025)*reveal(t,.1+i*.05,1.8)}/>)}</g></svg>;};
export const BackdropStage3:React.FC<{t:number;paper?:boolean;vision?:boolean;extra?:number}>=({t,paper=false,vision=false,extra=0})=><AbsoluteFill style={{background:paper?C.paper:`linear-gradient(180deg, ${C.deep} 0%, ${C.navy} 70%, #123B50 100%)`}}>{!paper&&<><div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse 90% 30% at 50% 90%, rgba(42,133,168,.22), transparent 75%)'}}/><Rings t={t} vision={vision} extra={extra}/><div style={{position:'absolute',left:0,right:0,top:868,height:1,background:'linear-gradient(90deg,transparent,rgba(244,238,226,.55),transparent)'}}/></>}</AbsoluteFill>;
const Frame:React.FC<{t:number;duration:number;paper?:boolean;transitionType:TransitionType;exitType:TransitionType;children:React.ReactNode}>=({t,duration,paper=false,transitionType,exitType,children})=>{const incoming=transitionType==='crossfade'?clamp(t/.3):1;const outgoing=t>duration?(exitType==='crossfade'?1-clamp((t-duration)/.3):0):1;return <AbsoluteFill style={{opacity:incoming*outgoing,color:paper?C.deep:C.paper}}>{children}</AbsoluteFill>;};
const BrandSmall:React.FC<{paper?:boolean}>=({paper=false})=><div style={{position:'absolute',top:66,left:112,width:330,height:92,opacity:paper?.90:.86}}><Img src={staticFile('brand/v10/宏泰.svg')} style={{width:'100%',height:'100%',objectFit:'contain',filter:paper?'none':'brightness(0) invert(1) drop-shadow(0 0 9px rgba(77,177,224,.26))'}}/></div>;
const Meta:React.FC<{children:React.ReactNode;paper?:boolean}>=({children,paper=false})=><Label light={paper} style={{position:'absolute',top:94,right:112,fontSize:20,letterSpacing:3,opacity:.65}}>{children}</Label>;
const Photo:React.FC<{file:string;t:number;style:React.CSSProperties;fit?:'cover'|'contain'}>=({file,t,style,fit='cover'})=><div style={{position:'absolute',overflow:'hidden',...style}}><Img src={staticFile(file)} style={{width:'100%',height:'100%',objectFit:fit,transform:fit==='contain'?'none':`scale(${1.04+Math.min(t,12)*.0025})`}}/></div>;
const OriginalDataScene:React.FC<{t:number;value:string;label:string;sub:string;index:string}>=({t,value,label,sub,index})=>{const p=reveal(t,.05,.9);return <><BrandSmall/><Meta>{index} / 集團實力</Meta><Label style={{position:'absolute',top:245,left:130}}>{label}</Label><div style={{position:'absolute',top:300,left:112,right:112,display:'flex',alignItems:'baseline',gap:30,transform:`translateY(${(1-p)*45}px) scale(${.94+.06*p})`,transformOrigin:'left center',opacity:p}}><span style={{...textStyle,fontSize:330,fontVariantNumeric:'tabular-nums',letterSpacing:'-.07em'}}>{value}</span></div><Label style={{position:'absolute',left:138,top:726,fontSize:34,letterSpacing:5}}>{sub}</Label><div style={{position:'absolute',left:135,top:809,width:1450,height:1,background:'linear-gradient(90deg,#2A85A8,transparent)'}}/><Label style={{position:'absolute',right:135,top:816,fontSize:19,letterSpacing:1,opacity:.5}}>集團數據 · 據公司介紹資料</Label></>;};
const DataScene:React.FC<{t:number;value:string;label:string;sub:string;index:string}>=props=>{
 const {t,value,label,sub,index}=props;if(index==='03')return <OriginalDataScene {...props}/>;
 const absolute=stage3Scenes.find(s=>s.id===(index==='01'?'premium':'commission'))!.start+t;
 const commission=index==='02',move=commission?reveal(t,0,.75):0;
 const selected=logoSpec.keep_ids.map(i=>providerLogos[i-1]);
 return <><BrandSmall/><Meta>{index} / 集團實力</Meta><Label style={{position:'absolute',left:135,top:260}}>{label}</Label><Title t={t} size={255} style={{position:'absolute',left:115,top:360,letterSpacing:'-.07em'}}>{value}</Title><Label style={{position:'absolute',left:135,top:720,fontSize:34}}>{sub}</Label>
 {!commission&&<Label style={{position:'absolute',left:1040,top:230,fontSize:19,letterSpacing:2,opacity:.6}}>香港保險產品供應商 · 據公司資料</Label>}
 <div style={{position:'absolute',inset:0,transform:`translateX(${-120*move}px)`,opacity:1-.55*move}}>{selected.map((file,i)=>{const lit=reveal(absolute,logoSpec.light_schedule[i].time,.18);return <Img key={file} src={staticFile(file)} style={{position:'absolute',left:1040+(i%5)*153,top:280+Math.floor(i/5)*92,width:142,height:80,objectFit:'contain',opacity:.14+.86*lit}}/>;})}</div>
 {commission&&<div style={{opacity:reveal(t,.3,.55)}}><Label style={{position:'absolute',left:1040,top:798,fontSize:19,letterSpacing:2,opacity:.75}}>銀行服務網絡 · 據公司資料</Label>{bankLogos.map((file,i)=><Img key={file} src={staticFile(file)} style={{position:'absolute',left:1040+i*370,top:842,width:340,height:75,objectFit:'contain',opacity:.9}}/>)}</div>}
 <Label style={{position:'absolute',left:137,top:825,fontSize:19,letterSpacing:1,opacity:.5}}>集團數據 · 據公司介紹資料</Label></>;
};

export const SceneContentV12Stage3:React.FC<{id:Stage3Id;t:number;globalTime:number;paper:boolean;variant?:'default'|'vision'|'trust';staticOffice?:boolean;hideOfficePhoto?:boolean}>=({id,t,globalTime,paper,variant='default',staticOffice=false,hideOfficePhoto=false})=><>

{id==='vision'&&<><BrandSmall/><Meta>每一個家族的未來</Meta><div style={{position:'absolute',left:130,top:346}}><Label style={{marginBottom:28,opacity:reveal(t,.6,1.2)}}>未來，值得更長遠的眼光</Label><Title t={t-.7} size={205}>看得更遠。</Title></div><div style={{position:'absolute',left:137,top:700,width:160*reveal(t,3.2,1.2),height:4,background:C.blue}}/></>}
{id==='origin'&&<><BrandSmall/><Meta>時間 · 專業 · 信任</Meta><Label style={{position:'absolute',left:134,top:252}}>集團源自</Label><Title t={t} size={360} style={{position:'absolute',left:112,top:300,color:C.paper,fontVariantNumeric:'tabular-nums'}}>1997<span style={{color:C.copper,fontSize:100,marginLeft:12}}>年</span></Title><Label style={{position:'absolute',left:139,top:748,fontSize:31,letterSpacing:3}}>一路走來，承接每一份信任。</Label></>}
{id==='premium'&&<DataScene t={t} value="100億+" label="集團總保費" sub="港元" index="01"/>}
{id==='commission'&&<DataScene t={t} value="15億+" label="集團總佣金" sub="港元" index="02"/>}
{id==='clients'&&<DataScene t={t} value="2萬+" label="高淨值客戶" sub="數字背後，是信任。" index="03"/>}
{id==='trust'&&<><BrandSmall/><Meta>專業的積累</Meta><Title t={t} size={104} style={{position:'absolute',left:130,top:174}}>每一份信任，都有分量。</Title><Label style={{position:'absolute',left:134,top:298,fontSize:25,letterSpacing:2,opacity:.65}}>業界肯定，見證專業積累</Label><AwardsStage3 t={t}/></>}
{id==='global'&&<><GeographicNetworkV12 time={sourceTimeStage3(globalTime)} sceneTime={t}/><BrandSmall/><Meta>全球視野 · 一路向前</Meta><Title t={t} size={96} style={{position:'absolute',left:128,top:190}}>讓眼光，跨越地域。</Title></>}
{id==='platform'&&<><BrandSmall/><Meta>家族辦公室平台</Meta><Title t={t} size={116} style={{position:'absolute',left:128,top:242}}>一個平台，連繫未來。</Title><svg width={1920} height={1080} style={{position:'absolute'}}><path d="M250 740 H1670 M960 740 V510" stroke={C.blue} strokeWidth={2} strokeDasharray={1700} strokeDashoffset={1700*(1-reveal(t,.2,1.6))} fill="none"/>{[250,605,960,1315,1670].map((x,i)=><g key={x} opacity={reveal(t,.4+i*.18,.7)}><circle cx={x} cy={740} r={7} fill={C.paper}/><path d={`M${x} 720 V700`} stroke={C.paper} strokeWidth={1.5}/></g>)}</svg><div style={{position:'absolute',left:710,top:430,width:500,height:160,background:C.paper,padding:22,boxSizing:'border-box',opacity:reveal(t,1,1)}}><Img src={staticFile('brand/v11/evergreen.svg')} style={{width:'100%',height:'100%',objectFit:'contain'}}/></div>{['保險','信託','稅務','教育','身份'].map((s,i)=><div key={s} style={{position:'absolute',left:150+i*355,top:770,width:200,textAlign:'center',...textStyle,fontSize:46,letterSpacing:3,opacity:reveal(t,.4+i*.18)}}>{s}</div>)}</>}
{id==='office'&&<><BrandSmall paper/><Meta paper>香港辦公室 · 公司實景</Meta>{!hideOfficePhoto&&<OfficePhotoStage3 t={t} still={staticOffice}/>}<Title t={t} size={115} style={{position:'absolute',left:125,top:342}}>看得全面。<br/>行得長遠。</Title><div style={{position:'absolute',left:132,top:715,width:110,height:4,background:C.blue}}/></>}
{id==='values'&&<><BrandSmall paper={paper}/><Meta paper={paper}>專業為本 · 穩健為根</Meta><Title t={t} size={143} style={{position:'absolute',left:variant==='trust'?210:130,top:variant==='trust'?420:360}}>{(variant==='vision'||(variant==='default'&&t<2.1))?'眼光，跨越地域。':'信任，扎根時間。'}</Title><div style={{position:'absolute',left:variant==='trust'?1100:139,top:variant==='trust'?750:715,display:'flex',flexDirection:variant==='trust'?'column':'row',gap:variant==='trust'?20:60,opacity:reveal(t,.4,1)}}><Label light={paper} style={{fontSize:24,letterSpacing:2}}>保監局持牌　FB1681</Label><Label light={paper} style={{fontSize:24,letterSpacing:2}}>PIBA會員　M0573</Label></div></>}
{id==='roots'&&<><BrandSmall paper/><Meta paper>根深 · 步穩 · 向前</Meta><Title t={t} size={126} style={{position:'absolute',left:125,top:340}}>根扎得深，<br/>長得更高。</Title><svg width={770} height={695} viewBox="480 390 310 280" style={{position:'absolute',left:1020,top:162}}><OfficialBrandV10 seconds={t*2.4} prefix="epic-tree-v11"/></svg></>}
{id==='close'&&<ClosingRevisionR01/>}
</>;
export const OfficePhotoStage3:React.FC<{t:number;still?:boolean}>=({t,still=false})=><div style={{position:'absolute',overflow:'hidden',left:748,top:258,width:1058,height:500}}><Img src={staticFile('stills/v11/hong-kong-office.jpg')} style={{width:'100%',height:'100%',objectFit:'cover',transform:still?'none':`scale(${1.04+Math.min(t,12)*.0025})`}}/></div>;
export const CaptionsStage3:React.FC<{time:number;paper:boolean;trust?:boolean}>=({time,paper,trust=false})=>{const caption=captions.find(c=>time>=c.start&&time<c.end+.12);return <>
 <div style={{position:'absolute',left:trust?900:105,right:105,...(trust?{top:278}:{bottom:58}),textAlign:trust?'right':'center',height:55,fontFamily:'Noto Sans TC',fontWeight:500,fontSize:trust?28:36,letterSpacing:1,color:paper?C.deep:C.paper,textShadow:paper?'none':'0 2px 12px rgba(0,0,0,.7)',opacity:caption?1:0}}>{caption?.text}</div>
 <div style={{position:'absolute',...(trust?{right:130,bottom:12}:{left:114,bottom:26}),fontFamily:'Noto Sans TC',fontSize:trust?14:16,letterSpacing:2,color:paper?C.deep:C.paper,opacity:.45}}>內部審片版 · 不作對外發布</div>
 </>;};
export const EpicFilmV12Stage3:React.FC=()=>{
 const actual=useCurrentFrame()/30,t=Math.min(actual,68.1);const active=stage3Scenes.filter(s=>t>=s.start).at(-1)!;const paper=paperAtStage3(active.id,t);
 return <AbsoluteFill style={{background:C.deep}}>
 <BackdropStage3 t={active.id==='trust'?Math.min(1,t-active.start):t-active.start} paper={paper} vision={active.id==='vision'} extra={active.id==='commission'?2:0}/>
 {stage3Scenes.map((s,i)=>{const prev=stage3Scenes[i-1],next=stage3Scenes[i+1];const enterType:TransitionType=prev&&paperAtStage3(prev.id,s.start-1/30)===paperAtStage3(s.id,s.start)?'crossfade':'cut';const exitType:TransitionType=next&&paperAtStage3(s.id,s.end-1/30)===paperAtStage3(next.id,next.start)?'crossfade':'cut';return <Sequence key={s.id} from={Math.round(s.start*30)} durationInFrames={Math.min(2103-Math.round(s.start*30),Math.round((s.end-s.start+(exitType==='crossfade'?.3:0))*30))}>
 <Frame t={(actual-s.start)} duration={s.end-s.start} paper={paperAtStage3(s.id,actual)} transitionType={enterType} exitType={exitType}>
 <SceneContentV12Stage3 id={s.id} t={Math.min(actual-s.start,s.id==='close'?7.4:100)} globalTime={actual} paper={paperAtStage3(s.id,actual)}/>
 </Frame></Sequence>;})}
 <CaptionsStage3 time={t} paper={paper} trust={active.id==='trust'}/>
 <Audio src={staticFile(epicV12Stage3.mix)}/>
 </AbsoluteFill>;
};
