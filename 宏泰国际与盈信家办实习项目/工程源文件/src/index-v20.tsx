import React from 'react';
import {Composition,registerRoot} from 'remotion';
import {EpicFilmV20} from './scenes/EpicFilmV20';
import cn from './config/timeline-v20-cn.json';
import yue from './config/timeline-v20-yue.json';
import en from './config/timeline-v20-en.json';
const Root=()=> <>{[yue,en,cn].map((timeline,i)=><Composition key={i} id={`BOI-HK-Epic-v20-${['YUE','EN','CN'][i]}`} component={EpicFilmV20} width={1920} height={1080} fps={30} durationInFrames={timeline.durationInFrames} defaultProps={{timeline,qa:false,muted:false}}/>)}</>;
registerRoot(Root);
