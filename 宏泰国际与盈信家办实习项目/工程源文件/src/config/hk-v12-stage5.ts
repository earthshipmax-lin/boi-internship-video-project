import {epicV12Stage3,stage3Scenes} from './hk-v12-stage3';
export const epicV12Stage5={...epicV12Stage3,composition:'BOI-HK-Epic-v12-Stage5'} as const;
export const stage5Timing={
 irisStart:1323,spreadFrames:33,holdFrames:3,officeContent:1359,
 officeExitStart:1476,valuesStart:1485,firstLine:1491,secondLine:1560,
 valuesExitStart:1644,rootsStart:1652,closeStart:1822,
} as const;
export const stage5Scenes=stage3Scenes.map(s=>({...s,
 start:s.id==='office'?1359/30:s.id==='values'?1485/30:s.start,
 end:s.id==='platform'?1359/30:s.id==='office'?1485/30:s.end,
}));
export const bankDisplayStage5={
 left:920,top:824,width:754,height:112,headingTop:778,
 visualInkHeight:54,sourceMargin:8,
 items:[
  {id:'minsheng',file:'stills/v12/bank-minsheng.jpg',sourceWidth:779,sourceHeight:171,ink:[11,19,747,149]},
  {id:'shanghai',file:'stills/v12/bank-shanghai.jpg',sourceWidth:850,sourceHeight:250,ink:[16,22,832,174]},
 ],
} as const;
