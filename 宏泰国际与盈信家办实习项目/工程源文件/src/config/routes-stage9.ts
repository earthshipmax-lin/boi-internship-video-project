import {citiesStage7,cubicRouteStage7,motionEaseStage7,XY} from './routes-stage7';

// The voice and subtitle track remain locked. Prompt12's 29-second starts
// conflict with its quoted narration, so cities retain their verified cues.
export const routeTimingStage9={
  sceneStart:864,sceneEnd:1141,hongKong:33.38,
  routes:[
    {name:'深圳',start:34.16,duration:.45,main:false,amplitude:5},
    {name:'紐約',start:34.52,duration:1.05,main:true,amplitude:8},
    {name:'新加坡',start:35.60,duration:.85,main:false,amplitude:5},
  ],
  arrivalRise:.12,arrivalReturn:.5,arrivalRing:.45,peakScale:1.06,
} as const;
export const modulationStage9={baseSamples:120,cycles:2.5,maxVertexStep:4.8,arcAuditStep:4.8} as const;
export const geographicBackgroundStage9={driftStart:2.8,driftEnd:6.2,driftPixels:40,landOpacityMin:.60,landOpacityMax:.68,opacityPeriod:3} as const;
export const citiesStage9=citiesStage7;
export type CityNameStage9=keyof typeof citiesStage9;
export const cityPointStage9=(name:CityNameStage9):XY=>[citiesStage9[name].xy[0],citiesStage9[name].xy[1]];
export const cubicRouteStage9=cubicRouteStage7;
export const motionEaseStage9=motionEaseStage7;
const diagonal=40/Math.sqrt(2);
// Label positions are in the same geographic group as land, paths and points.
// Only HK/SZ need the explicit 40px leader. No local enlargement is present.
export const labelsStage9={
  '香港':{dx:-diagonal-10,dy:diagonal+8,anchor:'end',leader:[-diagonal,diagonal]},
  '深圳':{dx:diagonal+10,dy:-diagonal-44,anchor:'start',leader:[diagonal,-diagonal]},
  '紐約':{dx:30,dy:26,anchor:'start',leader:null},
  '新加坡':{dx:30,dy:28,anchor:'start',leader:null},
} as const;
export const clampStage9=(v:number)=>Math.max(0,Math.min(1,v));
export const driftStage9=(sceneTime:number)=>{
  const p=clampStage9((sceneTime-geographicBackgroundStage9.driftStart)/(geographicBackgroundStage9.driftEnd-geographicBackgroundStage9.driftStart));
  return -geographicBackgroundStage9.driftPixels*(.5-.5*Math.cos(Math.PI*p));
};
export const arrivalStage9=(elapsed:number)=>{
  const rise=1-Math.pow(1-clampStage9(elapsed/routeTimingStage9.arrivalRise),3);
  const back=Math.pow(1-clampStage9((elapsed-routeTimingStage9.arrivalRise)/routeTimingStage9.arrivalReturn),5);
  const pulse=elapsed<0?0:elapsed<=routeTimingStage9.arrivalRise?rise:back;
  const ring=clampStage9(elapsed/routeTimingStage9.arrivalRing);
  return {scale:1+.06*pulse,radius:elapsed<0?5:elapsed<=routeTimingStage9.arrivalRise?5+4*rise:7+2*back,
    ringRadius:5+21*ring,ringOpacity:elapsed>=0&&elapsed<routeTimingStage9.arrivalRing?.6*(1-ring):0};
};
