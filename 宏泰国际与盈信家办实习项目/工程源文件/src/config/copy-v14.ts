import type {Locale,ScreenTextKeyV12} from './locale-v12';
import {getScreenTextV12} from './locale-v12';
import {getScreenCopyV13,type TextScreenCopyIdV13} from './screen-copy-v13';
import english from './english-narration-v14.json';
export const englishNarrationV14:Record<string,string>=english;
const screen:Partial<Record<ScreenTextKeyV12,string>>={
 visionTitle:'Look ahead.',visionSubtitle:"Your family's future deserves a long-term view.",
 awardsTitle:'Your trust means everything.',awardsSubtitle:'Recognized across the industry',
 platformTitle:'Expertise, connected.',valuesMeta:'Expertise. Care. Lasting trust.',
 peopleTitle:'Meet the people behind our expertise.',
};
const copy:Partial<Record<TextScreenCopyIdV13,string>>={
 'meta.vision':"Your family's future",'meta.origin':'Experience · Expertise · Trust',
 'meta.awards':'Experience, recognized','meta.platform':'A connected family office',
 'meta.offices':'Our offices · Three cities','origin.label':'Our roots',
 'origin.support':'Built on expertise and the trust of families.',
 'premium.label':'Total group premiums','commission.label':'Total group commission',
 'clients.support':'Behind every number is a family.',
 'map.title':'A wider world. A shared future.','map.singapore-status':'Plans underway',
 'offices.headline':'See the whole picture.\nPlan for the long term.',
 'offices.vision-title':'An outlook that crosses borders.',
 'values.title':'Trust grows over time.',
 'legal.licences':'Insurance Authority license FB1681 · PIBA member M0573',
 'legal.compliance':'Risk management · Compliance · Client privacy · Business continuity',
 'meta.roots':'Strong roots · Steady steps',
};
export const getScreenTextV14=(locale:Locale,key:ScreenTextKeyV12)=>locale==='en'?(screen[key]??getScreenTextV12(locale,key)):getScreenTextV12(locale,key);
export const getScreenCopyV14=(locale:Locale,key:TextScreenCopyIdV13)=>locale==='en'?(copy[key]??getScreenCopyV13(locale,key)):getScreenCopyV13(locale,key);
