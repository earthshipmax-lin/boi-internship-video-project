/** Candidate CSS colours from the Stage10 numeric preflight; actual-frame
 * contrast and land compositing still require the full-film browser audit. */
export const themeV13={deep:'#0B314A',navy:'#0F4668',bottom:'#10496C',land:'#2C789F',landStroke:'#6FB4D2',blue:'#2F97BE',paper:'#F4EEE2',copper:'#B9653F',ink:'#061C2B'} as const;
export type ThemeV13=typeof themeV13;
export const clampV13=(n:number)=>Math.max(0,Math.min(1,n));
export const easeV13=(n:number)=>1-Math.pow(1-clampV13(n),4);
export const revealV13=(time:number,start=0,duration=.85)=>easeV13((time-start)/duration);
