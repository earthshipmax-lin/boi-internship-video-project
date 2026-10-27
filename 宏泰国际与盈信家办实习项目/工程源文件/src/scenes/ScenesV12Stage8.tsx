import React from 'react';
import {AbsoluteFill,Audio,Img,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {EpicFilmV12Stage7} from './ScenesV12Stage7';
import {BackdropStage3,CaptionsStage3,SceneContentV12Stage3} from './ScenesV12Stage3';
import {AwardsStage8} from '../components/AwardsStage8';
import {GeographicNetworkStage7} from '../components/GeographicNetworkStage7';
import {epicV12Stage5} from '../config/hk-v12-stage5';
const C=epicV12Stage5.colors;
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
const ease=(x:number)=>1-Math.pow(1-clamp(x),4);
const text:React.CSSProperties={fontFamily:'Noto Sans TC',fontWeight:800,letterSpacing:'-.055em',lineHeight:1.12};
const Brand:React.FC=()=><div style={{position:'absolute',top:66,left:112,width:330,height:92,opacity:.86}}><Img src={staticFile('brand/v10/宏泰.svg')} style={{width:'100%',height:'100%',objectFit:'contain',filter:'brightness(0) invert(1) drop-shadow(0 0 9px rgba(77,177,224,.26))'}}/></div>;
const Meta:React.FC<{children:React.ReactNode}>=({children})=><div style={{position:'absolute',top:94,right:112,fontFamily:'Noto Sans TC',fontSize:20,fontWeight:500,letterSpacing:3,opacity:.65}}>{children}</div>;
const Title:React.FC<{t:number;top:number;size:number;children:React.ReactNode}>=({t,top,size,children})=>{const p=ease(t/.85);return <div style={{position:'absolute',left:130,top,...text,fontSize:size,opacity:p,transform:`translateY(${(1-p)*35}px)`}}>{children}</div>;};
const Trust:React.FC<{time:number}>=({time})=>{const t=time-23.5;return <>
  <Brand/><Meta>專業的積累</Meta>
  <Title t={t} top={174} size={88}>每一份信任，都有分量。</Title>
  <div style={{position:'absolute',left:134,top:280,fontFamily:'Noto Sans TC',fontSize:23,fontWeight:500,letterSpacing:2,opacity:.65}}>業界肯定，見證專業積累</div>
  <AwardsStage8 t={t}/>
</>;};
const Global:React.FC<{time:number;qa:boolean}>=({time,qa})=><>
  <GeographicNetworkStage7 time={time} sceneTime={time-923/30} qa={qa}/>
  <Brand/><Meta>全球視野 · 一路向前</Meta>
  <Title t={time-923/30} top={190} size={96}>讓眼光，跨越地域。</Title>
</>;
export const EpicFilmV12Stage8:React.FC<{qa?:boolean}>=({qa=false})=>{
  const frame=useCurrentFrame(),time=frame/30;
  if(frame<705||frame>=932)return <EpicFilmV12Stage7 qa={qa}/>;
  const global=frame>=923,anchor=global?923:705;
  const fade=clamp((frame-anchor)/9);
  return <AbsoluteFill style={{background:C.deep,color:C.paper}}>
    <BackdropStage3 t={global?time-923/30:Math.min(1,time-23.5)}/>
    {global?<>
      {fade<1&&<AbsoluteFill style={{opacity:1-fade}}><Trust time={time}/></AbsoluteFill>}
      <AbsoluteFill style={{opacity:fade}}><Global time={time} qa={qa}/></AbsoluteFill>
    </>:<>
      {fade<1&&<Sequence from={609}><AbsoluteFill style={{opacity:1-fade}}><SceneContentV12Stage3 id="clients" t={time-609/30} globalTime={time} paper={false}/></AbsoluteFill></Sequence>}
      <AbsoluteFill style={{opacity:fade}}><Trust time={time}/></AbsoluteFill>
    </>}
    <CaptionsStage3 time={time} paper={false}/>
    <Audio src={staticFile(epicV12Stage5.mix)}/>
  </AbsoluteFill>;
};
