import React from 'react';
import {AbsoluteFill,Audio,Img,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {BackdropStage3,CaptionsStage3,OfficePhotoStage3,SceneContentV12Stage3} from './ScenesV12Stage3';
import {Stage3Id} from '../config/hk-v12-stage3';
import {epicV12Stage5,stage5Timing as timing,stage5Scenes} from '../config/hk-v12-stage5';
import {providerLogos} from '../config/photos-v12';
import logos from '../config/logos-stage2.json';
import {BankNetworkStage5} from '../components/BankNetworkStage5';
import {RingIrisStage5} from '../components/RingIrisStage5';
const C=epicV12Stage5.colors;
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
const ease=(x:number)=>1-Math.pow(1-clamp(x),4);
const reveal=(t:number,start=0,d=.6)=>ease((t-start)/d);
const text:React.CSSProperties={fontFamily:'Noto Sans TC',fontWeight:800,letterSpacing:'-.055em',lineHeight:1.12};
const Brand:React.FC<{paper?:boolean}>=({paper=false})=><div style={{position:'absolute',top:66,left:112,width:330,height:92,opacity:paper?.9:.86}}><Img src={staticFile('brand/v10/宏泰.svg')} style={{width:'100%',height:'100%',objectFit:'contain',filter:paper?'none':'brightness(0) invert(1) drop-shadow(0 0 9px rgba(77,177,224,.26))'}}/></div>;
const Meta:React.FC<{children:React.ReactNode;paper?:boolean}>=({children,paper=false})=><div style={{position:'absolute',top:94,right:112,fontFamily:'Noto Sans TC',fontSize:20,fontWeight:500,letterSpacing:3,color:paper?C.deep:C.paper,opacity:.65}}>{children}</div>;
const Title:React.FC<{children:React.ReactNode;p:number;style?:React.CSSProperties}>=({children,p,style})=><div style={{position:'absolute',...text,opacity:p,transform:`translateY(${(1-p)*18}px)`,...style}}>{children}</div>;
const Commission:React.FC<{t:number}>=({t})=>{
 const move=1-Math.pow(1-clamp(t/.75),4),p=1-Math.pow(1-clamp(t/.85),4);
 return <><Brand/><Meta>02 / 集團實力</Meta>
 <div style={{position:'absolute',left:135,top:260,fontFamily:'Noto Sans TC',fontSize:28,fontWeight:500,letterSpacing:6}}>集團總佣金</div>
 <div style={{position:'absolute',left:115,top:360,...text,fontSize:255,letterSpacing:'-.07em',opacity:p,transform:`translateY(${(1-p)*35}px)`}}>15億+</div>
 <div style={{position:'absolute',left:135,top:720,fontFamily:'Noto Sans TC',fontSize:34,fontWeight:500,letterSpacing:5}}>港元</div>
 <div style={{position:'absolute',inset:0,transform:`translateX(${-120*move}px)`,opacity:1-.55*move}}>{logos.keep_ids.map((id,i)=><Img key={id} src={staticFile(providerLogos[id-1])} style={{position:'absolute',left:1040+i%5*153,top:280+Math.floor(i/5)*92,width:142,height:80,objectFit:'contain'}}/>)}</div>
 <BankNetworkStage5 t={t}/>
 <div style={{position:'absolute',left:137,top:825,fontFamily:'Noto Sans TC',fontSize:19,fontWeight:500,letterSpacing:1,opacity:.5}}>集團數據 · 據公司介紹資料</div>
 </>;
};
const Office:React.FC<{time:number}>=({time})=>{
 const p=reveal(time,timing.officeContent/30),out=1-ease((time-timing.officeExitStart/30)/.3);
 return <><Brand paper/><Meta paper>香港辦公室 · 公司實景</Meta>
 <div style={{position:'absolute',inset:0,opacity:out}}><OfficePhotoStage3 t={0} still/>
 <Title p={p} style={{left:125,top:342,fontSize:115}}>看得全面。<br/>行得長遠。</Title>
 <div style={{position:'absolute',left:132,top:715,width:110,height:4,background:C.blue}}/>
 </div></>;
};
const Values:React.FC<{time:number}>=({time})=>{
 const out=1-ease((time-timing.valuesExitStart/30)/((timing.rootsStart-timing.valuesExitStart)/30));
 return <><Brand paper/><Meta paper>專業為本 · 穩健為根</Meta>
 <div style={{position:'absolute',inset:0,opacity:out}}>
 <Title p={reveal(time,timing.firstLine/30)} style={{left:130,top:330,fontSize:138}}>眼光，跨越地域。</Title>
 <Title p={reveal(time,timing.secondLine/30)} style={{left:130,top:520,fontSize:143}}>信任，扎根時間。</Title>
 <div style={{position:'absolute',right:150,top:760,fontFamily:'Noto Sans TC',fontSize:24,fontWeight:500,letterSpacing:2,lineHeight:2,color:C.deep,opacity:.78*reveal(time,timing.firstLine/30)}}>保監局持牌　FB1681<br/>PIBA會員　M0573</div>
 </div></>;
};
type State={id:Stage3Id;start:number;paper:boolean};
const stateAt=(frame:number):State=>{const s=stage5Scenes.filter(s=>frame>=Math.round(s.start*30)).at(-1)!;return {id:s.id,start:s.start,paper:['office','values','roots','close'].includes(s.id)};};
const Content:React.FC<{state:State;time:number;opacity?:number}>=({state,time,opacity=1})=><Sequence from={Math.round(state.start*30)}><AbsoluteFill style={{opacity,color:state.paper?C.deep:C.paper}}>
 {state.id==='commission'?<Commission t={time-state.start}/>:state.id==='office'?<Office time={time}/>:state.id==='values'?<Values time={time}/>:<SceneContentV12Stage3 id={state.id} t={Math.max(0,time-state.start)} globalTime={time} paper={state.paper} staticOffice/>}
 </AbsoluteFill></Sequence>;
const Background:React.FC<{state:State;time:number}>=({state,time})=><BackdropStage3 t={state.id==='trust'?Math.min(1,time-state.start):Math.max(0,time-state.start)} paper={state.paper} vision={state.id==='vision'} extra={state.id==='commission'?2:0}/>;
const Snapshot:React.FC=()=>{const state=stateAt(timing.irisStart),time=timing.irisStart/30;return <AbsoluteFill><Background state={state} time={time}/><Content state={state} time={time}/><CaptionsStage3 time={time} paper={false}/></AbsoluteFill>;};
export const EpicFilmV12Stage5:React.FC=()=>{
 const frame=useCurrentFrame(),time=Math.min(frame/30,68.1),state=stateAt(frame);
 const iris=frame>=timing.irisStart&&frame<timing.officeContent;
 const i=stage5Scenes.findIndex(s=>s.id===state.id),s=stage5Scenes[i],prev=stage5Scenes[i-1];
 const sequential=['office','values','roots'].includes(state.id);
 const sameColor=prev&&!sequential&&stateAt(Math.round(s.start*30)-1).paper===state.paper;
 const fade=sameColor?clamp((time-s.start)/(state.id==='close'?.4:.3)):1;
 return <AbsoluteFill style={{background:'#000'}}><AbsoluteFill style={{opacity:Math.min(1,frame/12)}}>
 {iris?<RingIrisStage5 frame={frame-timing.irisStart} oldScene={<Snapshot/>} newBackground={<><BackdropStage3 t={0} paper/><OfficePhotoStage3 t={0} still/></>}/>:<>
  <Background state={state} time={time}/>
  {fade<1&&prev&&<Content state={stateAt(Math.round(s.start*30)-1)} time={time} opacity={1-fade}/>}
  <Content state={state} time={time} opacity={fade}/>
  <CaptionsStage3 time={time} paper={state.paper} trust={state.id==='trust'}/>
 </>}
 </AbsoluteFill><Audio src={staticFile(epicV12Stage5.mix)}/></AbsoluteFill>;
};
