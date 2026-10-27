import {stage3Scenes,epicV12Stage3} from './hk-v12-stage3';
export const epicV12Stage4={...epicV12Stage3,composition:'BOI-HK-Epic-v12-Stage4'} as const;
export const irisStage4={cx:960,cy:820,radius:1270,feather:60,edgeWidth:2,spreadFrames:18,holdFrames:12,totalFrames:30} as const;
const anchor=(id:string)=>Math.round(stage3Scenes.find(s=>s.id===id)!.start*30);
// Lead into the existing narration anchors, so the one-second iris/hold does
// not delay a new headline into the middle of its spoken sentence.
export const valuesTrustFrame=1564;
export const stage4Irises=[
 {id:'platform-office',from:'platform',to:'office',startFrame:anchor('office')-30,contentFrame:anchor('office'),paper:true,photo:true},
 {id:'office-values',from:'office',to:'values',startFrame:anchor('values')-30,contentFrame:anchor('values'),paper:false,photo:false},
 {id:'values-vision-trust',from:'values',to:'values',startFrame:valuesTrustFrame-30,contentFrame:valuesTrustFrame,paper:true,photo:false},
] as const;
