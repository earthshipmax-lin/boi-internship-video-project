import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {BackdropStage3,CaptionsStage3,OfficePhotoStage3,SceneContentV12Stage3} from './ScenesV12Stage3';
import {epicV12Stage4,irisStage4,stage4Irises,valuesTrustFrame} from '../config/hk-v12-stage4';
import {stage3Scenes,Stage3Id} from '../config/hk-v12-stage3';
import {RingIrisStage4} from '../components/RingIrisStage4';
type State={id:Stage3Id;start:number;paper:boolean;variant:'default'|'vision'|'trust'};
const stateAt=(frame:number):State=>{
 const s=stage3Scenes.filter(s=>frame>=Math.round(s.start*30)).at(-1)!;
 const trust=s.id==='values'&&frame>=valuesTrustFrame;
 return {id:s.id,start:trust?valuesTrustFrame/30:s.start,paper:['office','roots','close'].includes(s.id)||trust,variant:s.id==='values'?(trust?'trust':'vision'):'default'};
};
const Content:React.FC<{state:State;time:number;opacity?:number}>=({state,time,opacity=1})=><Sequence from={Math.round(state.start*30)}>
 <AbsoluteFill style={{opacity,color:state.paper?'#061C2B':'#F4EEE2'}}><SceneContentV12Stage3 id={state.id} t={Math.max(0,time-state.start)} globalTime={time} paper={state.paper} variant={state.variant} staticOffice/></AbsoluteFill>
</Sequence>;
const Background:React.FC<{state:State;time:number}>=({state,time})=><BackdropStage3 t={state.id==='trust'?Math.min(1,time-state.start):Math.max(0,time-state.start)} paper={state.paper} vision={state.id==='vision'} extra={state.id==='commission'?2:0}/>;
const Snapshot:React.FC<{frame:number}>=({frame})=>{const state=stateAt(frame),time=frame/30;return <AbsoluteFill><Background state={state} time={time}/><Content state={state} time={time}/><CaptionsStage3 time={time} paper={state.paper} trust={state.id==='trust'}/></AbsoluteFill>;};
export const EpicFilmV12Stage4:React.FC=()=>{
 const frame=useCurrentFrame(),time=Math.min(frame/30,68.1),phase=stage4Irises.find(s=>frame>=s.startFrame&&frame<s.contentFrame);
 const state=stateAt(frame);
 const sceneIndex=stage3Scenes.findIndex(s=>s.id===state.id),scene=stage3Scenes[sceneIndex],prev=stage3Scenes[sceneIndex-1];
 const sameColor=prev&&state.variant!=='trust'&&stateAt(Math.round(scene.start*30)-1).paper===state.paper;
 const fadeDuration=state.id==='close'?.4:.3;
 const fade=sameColor?Math.max(0,Math.min(1,(time-scene.start)/fadeDuration)):1;
 return <AbsoluteFill style={{background:'#000'}}>
 <AbsoluteFill style={{opacity:Math.min(1,frame/12)}}>
 {phase?<RingIrisStage4 frame={frame-phase.startFrame} paper={phase.paper} oldScene={<Snapshot frame={phase.startFrame}/>} newBackground={<>
  <BackdropStage3 t={0} paper={phase.paper}/>
  {phase.photo&&<OfficePhotoStage3 t={0} still/>}
 </>}/>:<>
  <Background state={state} time={time}/>
  {fade<1&&prev&&<Content state={stateAt(Math.round(scene.start*30)-1)} time={time} opacity={1-fade}/>}
  <Content state={state} time={time} opacity={fade}/>
  <CaptionsStage3 time={time} paper={state.paper} trust={state.id==='trust'}/>
 </>}
 </AbsoluteFill>
 <Audio src={staticFile(epicV12Stage4.mix)}/>
 </AbsoluteFill>;
};
