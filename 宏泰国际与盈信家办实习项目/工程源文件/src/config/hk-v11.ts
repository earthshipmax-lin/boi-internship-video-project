import beats from './beats-v11.json';
export const epicV11={width:1920,height:1080,fps:30,duration:68,composition:'BOI-HK-Epic-v11',voiceOffset:2.4,mix:'music/v11/review-mix-headroom.wav',colors:{navy:'#0B2E45',deep:'#061C2B',blue:'#2A85A8',paper:'#F4EEE2',copper:'#B9653F'}} as const;
// Minor timing adjustment to the closest measured transient where one is nearby.
const snap=(target:number)=>{const nearest=beats.onsets_s.reduce((best,n)=>Math.abs(n-target)<Math.abs(best-target)?n:best,target+99);return Math.abs(nearest-target)<.18?Math.round(nearest*30)/30:Math.round(target*30)/30;};
const starts=[0,6.08,14.35,17.5,20.3,23.5,28.6,35.95,43.2,47.6,52.85,58.55].map((v,i)=>i?snap(v):0);
const ids=['vision','origin','premium','commission','clients','trust','global','platform','office','values','roots','close'] as const;
export type EpicSceneId=typeof ids[number];
export const epicScenes=ids.map((id,i)=>({id,start:starts[i],end:starts[i+1]??68}));
