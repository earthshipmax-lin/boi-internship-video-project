import {hk} from './config/hk';
import {Film,SceneUnit,CaptionUnit,AudioTrack} from './Film';
export const WORKBENCH={
 name:'宏泰國際 · MiniMax粵語版',fps:hk.fps,width:hk.width,height:hk.height,total:Math.round(hk.duration*hk.fps),
 background:'oklch(97% 0.01 80)',revision:'boi-hk-minimax-v4',
 shots:hk.scenes.map(s=>({id:s.id,label:s.id,from:Math.round(s.start*hk.fps),duration:Math.round((s.end-s.start)*hk.fps),component:SceneUnit,props:{id:s.id},durationProp:'duration',schema:s.id==='S0'?[]:[{type:'text',key:'title',label:'主標題',default:s.title[0]}]})),
 captions:hk.scenes.filter(s=>s.id!=='S0').map(s=>({id:`caption-${s.id}`,label:`字幕 ${s.id}`,from:Math.round(s.start*hk.fps),duration:Math.round((s.end-s.start)*hk.fps),component:CaptionUnit,props:{id:s.id}})),
 overlays:[{id:'audio-track',label:'本地配音與音樂',from:0,duration:Math.round(hk.duration*hk.fps),component:AudioTrack,props:{bgm:true}}],
 transitions:[],sfx:[],bgm:[],order:['captions','overlays'],original:Film,
};
