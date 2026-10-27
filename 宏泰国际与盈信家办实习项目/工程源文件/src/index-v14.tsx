import React from 'react';
import {Composition,registerRoot} from 'remotion';
import {EpicFilmRefinedV14,type EpicFilmPropsV14} from './scenes/EpicFilmRefinedV14';
const Root=()=> <>{(['yue','en','zh-CN'] as const).map((locale,i)=><Composition key={locale} id={['BOI-HK-Epic-v14','BOI-HK-Epic-v14-EN','BOI-HK-Epic-v14-CN'][i]} component={EpicFilmRefinedV14} width={1920} height={1080} fps={30} durationInFrames={3426} defaultProps={{locale,timeline:null,qa:false,muted:false} as EpicFilmPropsV14} calculateMetadata={({props})=>({durationInFrames:props.timeline?.durationInFrames??3426})}/>)}</>;
registerRoot(Root);
