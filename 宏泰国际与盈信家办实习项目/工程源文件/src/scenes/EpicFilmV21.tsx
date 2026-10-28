import React from 'react';
import {AbsoluteFill,Audio,staticFile,useCurrentFrame} from 'remotion';
import {FilmPictureV21} from './ScenesV21';
export const EpicFilmV21:React.FC<{timeline:any;qa:boolean;muted:boolean}>=({timeline:t,qa,muted})=>{
 const f=useCurrentFrame(),r=t.frames[f],o=r.old,s=t.originalSceneStarts,e=t.edit,loc=t.locale;
 const caption=t.cues.find((c:any)=>f>=c.startFrame&&f<c.endFrame)?.text??null;
 const second=t.cues.find((c:any)=>c.id==='caption-22').startFrame;
 const exiting=f>=e.fadeStart&&f<e.rootsStart,p=exiting?Math.max(0,1-(f-e.fadeStart)/9):1;
 return <AbsoluteFill style={{background:'#F4EEE2'}}><AbsoluteFill style={{opacity:p,transform:exiting?`translateY(${-24*(1-p)}px)`:undefined}}>
 <FilmPictureV21 sourceFrame={r.source} locale={loc} watermark={false} qa={qa} captionText={caption} mapClock={{irisFrame:33*(o-s.iris)/Math.max(1,s.irisEnd-s.iris-3),time:o/30,sceneTime:(o-s.map)/30,timing:t.mapTiming,dataTime:(o-s.data)/30,platformTime:(o-s.platform)/30,rootsTime:(f-e.rootsStart)/30,closingTime:(o-s.closing)/30,rootsSecond:f>=second,rootsSecondTime:(f-second)/30}}/>
 </AbsoluteFill>{!muted&&<Audio src={staticFile(`music/hk-v20/${loc==='zh-CN'?'cn':loc}-master.wav`)}/>}</AbsoluteFill>;
};
