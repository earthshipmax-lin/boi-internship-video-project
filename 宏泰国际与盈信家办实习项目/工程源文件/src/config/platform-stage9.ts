/** Prompt12 adapted below the locked title and above the 967px caption lane.
 * Outer R400 uniformly reduced to R245. Inner R185 instead of uniform R128.625
 * preserves evidence legibility and makes semantic branches exactly 60px long.
 */
export type PlatformRectStage9={x:number;y:number;width:number;height:number};
export const platformStage9={
 canvas:{width:1920,height:1080},
 title:{x:128,y:242,fontSize:116,width:1570,height:130,maxEntryOffset:35,text:'一個平台，連繫未來。'},
 center:{x:960,y:674},outerRadius:245,innerRadius:185,
 nominalSectorDegrees:120,sectorGapDegrees:6,nodeStepDegrees:72,branchLength:60,
 tree:{x:908,y:622,width:104,height:104},
 evergreen:{x:560,y:671,width:180,height:180,logo:{x:575,y:739.8,width:150,height:42.4},source:'brand/v11/evergreen.svg'},
 captionSafeTop:967,contentSafeBottom:940,
 animation:{treeStart:0,treeDuration:.3,arcStart:.3,arcDuration:.25,arcStagger:.18,nodeStart:1.2,nodeDuration:.3,nodeStagger:.12,evergreenStart:2.4,evergreenDuration:.4,staticFrom:2.8},
 sectors:[
  {id:'insurance',title:'核心保險業務',nominalStart:-150,nominalEnd:-30,start:-147,end:-33,titleRect:{x:875,y:535,width:170,height:32},evidenceRect:{x:866,y:578,width:188,height:40},evidence:['香港 · 澳門 · 美國','百慕達 · 新加坡'],evidenceFontSize:18},
  {id:'wealth',title:'財富管理',nominalStart:-30,nominalEnd:90,start:-27,end:87,titleRect:{x:993,y:724,width:120,height:32},evidenceRect:{x:990,y:758,width:108,height:36},evidence:['信託 · 遺產','稅務規劃'],evidenceFontSize:16},
  {id:'family',title:'家族辦公室',nominalStart:90,nominalEnd:210,start:93,end:207,titleRect:{x:811,y:724,width:151,height:32},evidenceRect:{x:815,y:760,width:146,height:20},evidence:['盈信家辦 EVERGREEN'],evidenceFontSize:15.5},
 ],
 nodes:[
  {id:'insurance',text:'保險',angle:-90,sector:'insurance',label:{x:910,y:386,width:100,height:38}},
  {id:'trust',text:'信託',angle:-18,sector:'wealth',label:{x:1238,y:578,width:100,height:38}},
  {id:'tax',text:'稅務',angle:54,sector:'wealth',label:{x:1054,y:891,width:100,height:38}},
  {id:'education',text:'教育',angle:126,sector:'family',label:{x:766,y:891,width:100,height:38}},
  {id:'identity',text:'身份',angle:198,sector:'family',label:{x:582,y:578,width:100,height:38}},
 ],
 source:{pdf:'宏泰国际公司介紹_SC_2026年10月14日.pdf',page:14,promptPageCorrection:'Prompt12 calls this page13; the actual three-business platform appears on PDF page14.',hierarchy:'Insurance services belong to core insurance; trust and tax to wealth management; education and identity to family affairs. Evergreen is attached to the family-office platform, not a separate fourth business.'},
} as const;
export const platformPolarStage9=(radius:number,angle:number)=>({x:platformStage9.center.x+radius*Math.cos(angle*Math.PI/180),y:platformStage9.center.y+radius*Math.sin(angle*Math.PI/180)});
export const platformArcStage9=(radius:number,start:number,end:number)=>{
 const a=platformPolarStage9(radius,start),b=platformPolarStage9(radius,end);
 return `M${a.x} ${a.y} A${radius} ${radius} 0 ${end-start>180?1:0} 1 ${b.x} ${b.y}`;
};
export const platformGeometryStage9={
 ...platformStage9,
 titleMaxMotionBox:{x:128,y:242,width:1570,height:165},
 ringBox:{x:715,y:429,width:490,height:490},
 treeSourceViewBox:'8.8875 8.0655 95.75112751258398 76.3045',
 officialSourceSha256:'1c0afe640258a0f04eb0c0c8f2ec29d6e5e23f8fe9853672731a9cdc0c45fc5a',
 sectors:platformStage9.sectors.map(s=>({...s,nominalDegrees:s.nominalEnd-s.nominalStart,drawnDegrees:s.end-s.start,arcLength:185*(s.end-s.start)*Math.PI/180})),
 nodes:platformStage9.nodes.map((n,index)=>({...n,point:platformPolarStage9(245,n.angle),branchStart:platformPolarStage9(185,n.angle),startTime:1.2+index*.12,settledTime:1.5+index*.12})),
 evergreenConnector:{start:platformPolarStage9(185,150),end:{x:740,y:766.5}},
} as const;
