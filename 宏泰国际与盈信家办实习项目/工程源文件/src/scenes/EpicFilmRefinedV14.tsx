import React from 'react';
import {AbsoluteFill,Audio,staticFile,useCurrentFrame} from 'remotion';
import {FilmPictureRefinedV14} from './ScenesRefinedV14';
import {PeopleAccordionV14} from '../components/PeopleAccordionV14';
import {pictureFrameV13} from '../config/timeline-v13';
import type {Locale} from '../config/locale-v12';
export type TimelineV14={locale:Locale;fps:number;durationInFrames:number;durationSeconds:number;map:{newStart:number;newEnd:number;oldStart:number;oldEnd:number}[];cues:{id:string;startFrame:number;endFrame:number;text:string}[];oldTimeline:any;sceneStarts:Record<string,number>;mapTiming:any;status:string};
export type EpicFilmPropsV14={locale:Locale;timeline:TimelineV14|null;qa:boolean;muted:boolean};
export const oldFrameV14=(f:number,t:TimelineV14)=>{const s=t.map.find(s=>f>=s.newStart&&f<s.newEnd)??t.map[t.map.length-1];return s.oldStart+(f-s.newStart)*(s.oldEnd-s.oldStart)/(s.newEnd-s.newStart);};
export const EpicFilmRefinedV14:React.FC<EpicFilmPropsV14>=({locale,timeline:t,qa,muted})=>{
 const frame=useCurrentFrame();if(!t)throw new Error('Measured V14 timeline required');
 let original=oldFrameV14(frame,t);for(const c of t.oldTimeline.redesignCuts){if(original>=c.startFrame)original+=c.frames;else break;}
 const view=pictureFrameV13(original,t.oldTimeline.sourceTimeline),caption=t.cues.find(c=>frame>=c.startFrame&&frame<c.endFrame)?.text??null;
 const rootsSecond=t.cues.find(c=>c.id==='caption-22')?.startFrame??0;
 return <AbsoluteFill>
 {view.kind==='people'?<PeopleAccordionV14 frame={view.frame} plan={t.oldTimeline.peoplePlan} locale={locale} qa={qa} captionText={caption}/>:<FilmPictureRefinedV14 sourceFrame={view.frame} locale={locale} qa={qa} captionText={caption} mapClock={{time:frame/30,sceneTime:(frame-t.sceneStarts.map)/30,timing:t.mapTiming,dataTime:(frame-t.sceneStarts.data)/30,platformTime:(frame-t.sceneStarts.platform)/30,rootsTime:(frame-t.sceneStarts.roots)/30,closingTime:(frame-t.sceneStarts.closing)/30,rootsSecond:frame>=rootsSecond,rootsSecondTime:(frame-rootsSecond)/30}}/>}
 {!muted&&<Audio src={staticFile(`music/hk-v14/${locale==='zh-CN'?'cn':locale}-master.wav`)}/>}
 </AbsoluteFill>;
};
