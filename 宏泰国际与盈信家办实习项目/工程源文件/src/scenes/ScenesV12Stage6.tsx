import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {EpicFilmV12Stage5} from './ScenesV12Stage5';
import {BackdropStage3, CaptionsStage3, SceneContentV12Stage3} from './ScenesV12Stage3';
import {epicV12Stage5} from '../config/hk-v12-stage5';
import {logoGridV12 as g} from '../config/logo-optical-v12';
import {LogoGridV12} from '../components/LogoGridV12';
const C = epicV12Stage5.colors;
const clamp = (v:number) => Math.max(0,Math.min(1,v));
const ease = (v:number) => 1-Math.pow(1-clamp(v),4);
const type:React.CSSProperties = {fontFamily:'Noto Sans TC',fontWeight:800,letterSpacing:'-.07em',lineHeight:1};

const Brand:React.FC = () => <div style={{position:'absolute',top:66,left:112,width:330,height:92,opacity:.86}}><Img src={staticFile('brand/v10/宏泰.svg')} style={{width:'100%',height:'100%',objectFit:'contain',filter:'brightness(0) invert(1) drop-shadow(0 0 9px rgba(77,177,224,.26))'}}/></div>;
const DataRings:React.FC<{frame:number}> = ({frame}) => {
  const t=(frame-g.premiumStartFrame)/30,commission=frame>=g.commissionStartFrame;
  return <svg width={1920} height={1080} style={{position:'absolute',inset:0}}><g opacity={.24}>
    {Array.from({length:commission?10:8},(_,i) => {
      const p=i<8?ease((t-.1-i*.05)/1.8):ease((frame-g.commissionStartFrame)/(30*.5));
      const r=140+i*115+t*3;
      return <ellipse key={i} cx={960} cy={820} rx={r} ry={r*.53} fill="none" stroke={i>=8?C.paper:i%3===0?C.paper:C.blue} strokeWidth={i>=8?1.4:i%3===0?1.1:.7} opacity={(i>=8?.65:.65-i*.025)*p}/>;
    })}
  </g></svg>;
};
const DataCopy:React.FC<{frame:number}> = ({frame}) => {
  const commission=frame>=g.commissionStartFrame;
  const p=ease((frame-(commission?g.commissionStartFrame:g.premiumStartFrame))/(30*.7));
  const premiumOut=commission?1:1-ease((frame-519)/6);
  return <>
    <div style={{position:'absolute',top:94,right:112,fontFamily:'Noto Sans TC',fontSize:20,fontWeight:500,letterSpacing:3,color:C.paper,opacity:.65}}>{commission?'02':'01'} / 集團實力</div>
    <div style={{position:'absolute',left:130,top:300,fontFamily:'Noto Sans TC',fontSize:28,fontWeight:500,letterSpacing:6}}>集團總{commission?'佣金':'保費'}</div>
    <div style={{position:'absolute',left:130,top:348,...type,fontSize:commission?300:260,opacity:p*premiumOut,transform:`translateY(${(1-p)*18}px)`}}>{commission?'15億+':'100億+'}</div>
    <div style={{position:'absolute',left:130,top:660,fontFamily:'Noto Sans TC',fontSize:34,fontWeight:500,letterSpacing:5}}>港元</div>
    <div style={{position:'absolute',left:130,top:700,fontFamily:'Noto Sans TC',fontSize:18,fontWeight:500,color:'#7A8A93',opacity:.55}}>據公司介紹資料</div>
  </>;
};
const DataContent:React.FC<{frame:number}> = ({frame}) => <><Brand/><DataCopy frame={frame}/><LogoGridV12 frame={frame}/></>;

export const EpicFilmV12Stage6:React.FC = () => {
  const frame=useCurrentFrame(),time=frame/30;
  // All other frames run the exact prior composition. Include the first nine
  // client frames so its outgoing crossfade cannot resurrect the old bank strip.
  if(frame<g.premiumStartFrame || frame>=g.clientsStartFrame+9) return <EpicFilmV12Stage5/>;
  const clients=frame>=g.clientsStartFrame;
  const fade=clamp((frame-(clients?g.clientsStartFrame:g.premiumStartFrame))/9);
  return <AbsoluteFill style={{background:C.deep,color:C.paper}}>
    <BackdropStage3 t={clients?(frame-g.clientsStartFrame)/30:0}/>
    {!clients&&<DataRings frame={frame}/>}
    {clients ? <>
      <AbsoluteFill style={{opacity:1-fade}}><DataContent frame={frame}/></AbsoluteFill>
      <Sequence from={g.clientsStartFrame}><AbsoluteFill style={{opacity:fade}}><SceneContentV12Stage3 id="clients" t={time-g.clientsStartFrame/30} globalTime={time} paper={false}/></AbsoluteFill></Sequence>
    </> : <>
      {fade<1&&frame<g.commissionStartFrame&&<Sequence from={182}><AbsoluteFill style={{opacity:1-fade}}><SceneContentV12Stage3 id="origin" t={time-182/30} globalTime={time} paper={false}/></AbsoluteFill></Sequence>}
      <AbsoluteFill style={{opacity:fade}}><DataContent frame={frame}/></AbsoluteFill>
    </>}
    <CaptionsStage3 time={time} paper={false}/>
    <Audio src={staticFile(epicV12Stage5.mix)}/>
  </AbsoluteFill>;
};
