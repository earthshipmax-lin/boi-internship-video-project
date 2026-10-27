import {epicV12,epicScenesV12} from './hk-v12';
export const STAGE3_SHIFT_FRAMES=63;
export const stage3Scenes=epicScenesV12.map(s=>({
 ...s,start:s.start+(s.start>=28.6?2.1:0),end:s.end+(s.end>=28.6?2.1:0),
}));
export type Stage3Id=typeof stage3Scenes[number]['id'];
export const epicV12Stage3={...epicV12,duration:70.1,durationInFrames:2103,composition:'BOI-HK-Epic-v12-Stage3',mix:'music/v12-stage3/review-mix.wav'} as const;
export const sourceTimeStage3=(time:number)=>time>=30.76666666?time-2.1:Math.min(time,28.6666666667);
export const paperAtStage3=(id:Stage3Id,time:number)=>['office','roots','close'].includes(id)||(id==='values'&&time>=54.1);
