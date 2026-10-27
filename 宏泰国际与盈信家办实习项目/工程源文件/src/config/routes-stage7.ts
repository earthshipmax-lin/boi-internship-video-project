import world from '../assets/world-v12.json';
export type XY = readonly [number,number];
export const routeTimingStage7 = {
  sceneStart:923,sceneEnd:1141,sourceShift:2.1,
  hongKong:33.38,labelDelay:.12,arrivalSeconds:.4,minimumStagger:.18,
  routes:[
    {name:'深圳',start:34.16,duration:.45,main:false},
    {name:'紐約',start:34.52,duration:.95,main:true},
    {name:'新加坡',start:35.60,duration:.80,main:false},
  ],
} as const;
export const cubicRouteStage7 = (a:XY,b:XY) => {
  const dx=b[0]-a[0],dy=b[1]-a[1],length=Math.hypot(dx,dy);
  let nx=-dy/(length||1),ny=dx/(length||1);
  if(ny>0){nx=-nx;ny=-ny;}
  const k=length*.18;
  const p1:[number,number]=[a[0]+dx*.28+nx*k,a[1]+dy*.28+ny*k];
  const p2:[number,number]=[a[0]+dx*.72+nx*k,a[1]+dy*.72+ny*k];
  return {start:a,end:b,p1,p2,d:`M${a[0]} ${a[1]} C${p1[0]} ${p1[1]} ${p2[0]} ${p2[1]} ${b[0]} ${b[1]}`};
};
export const regionalPointStage7 = (lon:number,lat:number):[number,number] => [195+(lon-113.7)/.85*340,750+(.8-(lat-22))/.8*150];
export const citiesStage7=world.cities;
export const motionEaseStage7=(x:number) => {
  if(x<=0)return 0;if(x>=1)return 1;
  let lo=0,hi=1;
  for(let i=0;i<24;i++){const t=(lo+hi)/2,bx=3*(1-t)**2*t*.4+3*(1-t)*t*t*.2+t*t*t;if(bx<x)lo=t;else hi=t;}
  const t=(lo+hi)/2;return 3*t*t-2*t*t*t;
};
