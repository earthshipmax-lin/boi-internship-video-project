import {Easing} from 'remotion';
export const theme = {
  color: {paper:'oklch(97% 0.01 80)', warmGray:'#e9e5df', ink:'oklch(25% 0.01 60)', muted:'#81796f', terracotta:'oklch(62% 0.13 45)', line:'#cfc7bb'},
  font: {serif:'"Noto Serif TC", "Source Serif 4"', sans:'"Noto Sans TC", Geist', latin:'Geist', latinSerif:'"Source Serif 4"'},
  type: {caption:32, subheading:32*1.333, heading:32*1.333**2, title:32*1.333**3, display:32*1.333**5},
  space: {unit:8, safeX:144, safeY:96, captionBottom:72},
  ease: Easing.bezier(0.16,1,0.3,1),
  microDuration:.5,
} as const;
export const clamp01=(x:number)=>Math.max(0,Math.min(1,x));
// Original logo easing is intentionally kept exactly as approved.
export const logoEase=(x:number)=>1-Math.pow(1-clamp01(x),4);
export const progress=(t:number,start:number,duration:number)=>logoEase((t-start)/duration);
export const reveal=(t:number,start=0,duration=.5)=>theme.ease(clamp01((t-start)/duration));
