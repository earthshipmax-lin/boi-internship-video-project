/** Production complete. Measured timelines are authoritative. */
export const peopleV13 = {
 status:'complete_prompt15_pending_user_film_review',
 insertBeforeOriginalFrame:1652,
 audioInsertBeforeOriginalFrame:1640,
 finalExtraFrames:911,
 finalTotalFrames:3426,
 originalFrames:2103,
 fps:30,
 minPersonFrames:72,
 minWallFrames:90,
 photoLayout:{left:130,width:1660,gap:8,count:6,equalWidth:270,focusWidth:900,otherWidth:144},
 transition:{delayFrames:6,durationFrames:15,bezier:[.16,1,.3,1] as const},
 nativeScaleLimit:1.6,
 approvedLowResolutionLayout:'native_aspect_warm_gray_contain_peak_scale_lte_1_6',
 voiceSamplesApproved:true,
 notes:[
  'Original office and trust pages precede insertion; roots and ending shift together.',
  '900 + 5*144 + 5*8 =1660; focus grow ratio is6.25, not4.',
  'Provisional visual study uses photo260-830, text850-1008, caption1018-1066; final VO plan requires a new full-frame audit.',
  'User approved warm-gray contain; measured people insertion911frames; Prompt15 total3426frames.',
 ],
} as const;

const clamp=(x:number)=>Math.max(0,Math.min(1,x));
/** Invert CSS cubic-bezier x; return its y, rather than evaluating y directly. */
export const peopleCurveV13=(time:number)=>{
 const x=clamp(time);if(x===0||x===1)return x;
 const cubic=(t:number,a:number,b:number)=>3*(1-t)*(1-t)*t*a+3*(1-t)*t*t*b+t*t*t;
 let lo=0,hi=1;
 for(let i=0;i<40;i++){const m=(lo+hi)/2;if(cubic(m,.16,.3)<x)lo=m;else hi=m;}
 return cubic((lo+hi)/2,1,1);
};

/** Largest-remainder rounding preserves all1660px, including the five8px gaps. */
const wholeWidths=(raw:number[])=>{
 const ints=raw.map(Math.floor),missing=1620-ints.reduce((a,b)=>a+b,0);
 const order=raw.map((v,i)=>({i,fraction:v-ints[i]})).sort((a,b)=>b.fraction-a.fraction||a.i-b.i);
 for(let i=0;i<missing;i++)ints[order[i].i]++;
 return ints;
};
const target=(focus:number|null)=>Array.from({length:6},(_,i)=>focus===null?270:i===focus?900:144);

/** Single shared progress controls every photo property; no per-photo stagger. */
export const peopleFocusStateV13=(from:number|null,to:number|null,elapsedFrames:number)=>{
 for(const i of [from,to])if(i!==null&&(!Number.isInteger(i)||i<0||i>=6))throw new Error('Invalid focus index');
 const progress=peopleCurveV13((elapsedFrames-6)/15),a=target(from),b=target(to);
 const widths=wholeWidths(a.map((v,i)=>v+(b[i]-v)*progress));
 let x=130;
 const items=widths.map((width,i)=>{
  const oldFocus=from===i?1:0,newFocus=to===i?1:0,focus=oldFocus+(newFocus-oldFocus)*progress;
  const item={index:i,left:x,width,focus,grayscale:1-focus,opacity:.55+.45*focus,scale:1.04-.04*focus};
  x+=width+8;return item;
 });
 return {progress,items,totalWidth:widths.reduce((m,n)=>m+n,0)+5*8,right:x-8};
};
