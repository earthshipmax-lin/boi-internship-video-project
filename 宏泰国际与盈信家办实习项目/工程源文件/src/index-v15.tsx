import React from 'react';
import {Composition,registerRoot} from 'remotion';
import {EpicFilmPolishedV15,type EpicFilmPropsV14} from './scenes/EpicFilmPolishedV15';
const Root=()=> <>{(['yue','en','zh-CN'] as const).map((locale,i)=><Composition key={locale} id={['BOI-HK-Epic-v15','BOI-HK-Epic-v15-EN','BOI-HK-Epic-v15-CN'][i]} component={EpicFilmPolishedV15} width={1920} height={1080} fps={30} durationInFrames={3426} defaultProps={{locale,timeline:null,qa:false,muted:false} as EpicFilmPropsV14} calculateMetadata={({props})=>({durationInFrames:props.timeline?.durationInFrames??3426})}/>)}</>;
registerRoot(Root);
