import React from 'react';
import {Audio,Sequence,staticFile} from 'remotion';
import {USTeamV1} from './USTeamV1';
export const USTeamVoiceB:React.FC=()=> <>
 <USTeamV1/>
 <Sequence from={24}>
  <Audio src={staticFile('vo/us-v1/team-b/VO-01.wav')} playbackRate={1} volume={1}/>
 </Sequence>
</>;
