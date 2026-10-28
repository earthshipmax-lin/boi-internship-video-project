import React from 'react';
import {Composition,registerRoot} from 'remotion';
import {EpicFilmV21} from './scenes/EpicFilmV21';
import cn from './config/timeline-v21-cn.json';
import yue from './config/timeline-v21-yue.json';
import en from './config/timeline-v21-en.json';
const Root=()=> <>{[yue,en,cn].map((timeline,i)=><Composition key={i} id={`BOI-HK-Epic-v21-${['YUE','EN','CN'][i]}`} component={EpicFilmV21} width={1920} height={1080} fps={30} durationInFrames={timeline.durationInFrames} defaultProps={{timeline,qa:false,muted:false}}/>)}</>;
registerRoot(Root);
