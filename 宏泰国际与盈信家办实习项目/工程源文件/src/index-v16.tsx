import React from 'react';
import {Composition,registerRoot} from 'remotion';
import {EpicFilmEndingV16,type EpicFilmPropsV14} from './scenes/EpicFilmEndingV16';
const Root=()=> <>{(['zh-CN'] as const).map((locale,i)=><Composition key={locale} id={'BOI-HK-Epic-v16-CN'} component={EpicFilmEndingV16} width={1920} height={1080} fps={30} durationInFrames={3426} defaultProps={{locale,timeline:null,qa:false,muted:false} as EpicFilmPropsV14} calculateMetadata={({props})=>({durationInFrames:props.timeline?.durationInFrames??3426})}/>)}</>;
registerRoot(Root);
