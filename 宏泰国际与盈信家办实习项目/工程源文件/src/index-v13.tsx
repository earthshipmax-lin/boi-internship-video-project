import React from 'react';
import {Composition,registerRoot} from 'remotion';
import {EpicFilmV13,type EpicFilmPropsV13} from './scenes/EpicFilmV13';
import type {Locale} from './config/locale-v12';
const versions:[string,Locale][]=[['BOI-HK-Epic-v13','yue'],['BOI-HK-Epic-v13-EN','en'],['BOI-HK-Epic-v13-CN','zh-CN']];
registerRoot(()=><>{versions.map(([id,locale])=><Composition key={id} id={id} component={EpicFilmV13} width={1920} height={1080} fps={30} durationInFrames={1} defaultProps={{locale,timeline:null,qa:false,muted:false} as EpicFilmPropsV13} calculateMetadata={({props})=>{if(!props.timeline)throw Error('Supply measured timeline from assemble-hk-v13.py');return {durationInFrames:props.timeline.durationInFrames};}}/>)}</>);
