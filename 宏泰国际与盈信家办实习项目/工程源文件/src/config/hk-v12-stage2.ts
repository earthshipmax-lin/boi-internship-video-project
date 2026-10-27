import {epicV12,epicScenesV12} from './hk-v12';
export type Stage2Id=typeof epicScenesV12[number]['id'];
export type TransitionType='cut'|'crossfade';
export const epicV12Stage2={...epicV12,composition:'BOI-HK-Epic-v12-Stage2'} as const;
// Preserve all accepted narration/subtitle/route cues. Section 5 contains
// conflicting example times; apply its explicit continuous-paper-after-52 goal.
export const paperAtStage2=(id:Stage2Id,time:number)=>['office','roots','close'].includes(id)||(id==='values'&&time>=52);
export const stage2Scenes=epicScenesV12.map((s,i)=>{
 const prev=epicScenesV12[i-1],next=epicScenesV12[i+1];
 const enterType:TransitionType=prev&&paperAtStage2(prev.id,s.start-1/30)===paperAtStage2(s.id,s.start)?'crossfade':'cut';
 const exitType:TransitionType=next&&paperAtStage2(s.id,s.end-1/30)===paperAtStage2(next.id,next.start)?'crossfade':'cut';
 return {...s,enterType,exitType};
});
