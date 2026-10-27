import React from 'react';
import {AbsoluteFill,Audio,staticFile,useCurrentFrame} from 'remotion';
import {FilmPictureV13} from './ScenesV13';
import {PeopleAccordionV13} from '../components/PeopleAccordionV13';
import {captionAtV13,pictureFrameV13,type TimelineV13} from '../config/timeline-v13';
import type {Locale} from '../config/locale-v12';
export type EpicFilmPropsV13={locale:Locale;timeline:TimelineV13|null;qa:boolean;muted:boolean;audioFolder?:string};
export const EpicFilmV13:React.FC<EpicFilmPropsV13>=({locale,timeline,qa,muted,audioFolder='hk-v13'})=>{
 const frame=useCurrentFrame();if(!timeline)throw new Error('Measured final timeline is required; no provisional film can be rendered.');
 const view=pictureFrameV13(frame,timeline),caption=captionAtV13(frame,timeline,locale),folder=locale==='zh-CN'?'cn':locale;
 return <AbsoluteFill>
  {view.kind==='people'?<PeopleAccordionV13 frame={view.frame} plan={timeline.peoplePlan} locale={locale} qa={qa} captionText={caption}/>:<FilmPictureV13 sourceFrame={view.frame} locale={locale} qa={qa} captionText={caption} mapClock={timeline.mapTiming?{time:frame/30,sceneTime:frame/30-(timeline.mapSceneStartSeconds??0),timing:timeline.mapTiming}:undefined}/>}
  {!muted&&<Audio src={staticFile(`music/${audioFolder}/${folder}-master.wav`)}/>}
 </AbsoluteFill>;
};
