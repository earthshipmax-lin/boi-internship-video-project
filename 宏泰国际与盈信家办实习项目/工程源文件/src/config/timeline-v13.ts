import type {Locale,LocalizedText} from './locale-v12';
import type {PeopleVisualPlanV13} from '../components/PeopleAccordionV13';
import type {RouteTimingV13} from '../components/GeographicNetworkV13';
export type TimelineV13={mapTiming?:RouteTimingV13;mapSceneStartSeconds?:number;fps:number;durationInFrames:number;durationSeconds:number;originalFrames:number;bodyExtraFrames:number;peopleFrames:number;peopleStartFrame:number;peopleSourceFrame:number;peoplePlan:PeopleVisualPlanV13;holds:{sourceFrame:number;frames:number;cueId:string;startFrame:number}[];cues:{id:string;startFrame:number;text:LocalizedText;duration:Record<Locale,number>}[]};
export const pictureFrameV13=(frame:number,t:TimelineV13):{kind:'base'|'people';frame:number}=>{
 if(frame>=t.peopleStartFrame&&frame<t.peopleStartFrame+t.peopleFrames)return {kind:'people',frame:frame-t.peopleStartFrame};
 let f=frame-(frame>=t.peopleStartFrame+t.peopleFrames?t.peopleFrames:0),shift=0;
 for(const h of t.holds){const start=h.sourceFrame+shift;if(f<start)break;if(f<start+h.frames)return {kind:'base',frame:h.sourceFrame};shift+=h.frames;}
 return {kind:'base',frame:Math.min(t.originalFrames-1,Math.max(0,f-shift))};
};
export const captionAtV13=(frame:number,t:TimelineV13,locale:Locale)=>t.cues.find(c=>frame>=c.startFrame&&frame<c.startFrame+c.duration[locale]*t.fps+3)?.text[locale]??null;
