import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderMedia,renderStill} from '@remotion/renderer';
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import path from 'node:path';
const q='qa/v14',exe='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';mkdirSync(q+'/frames',{recursive:true});
const url=await bundle({entryPoint:path.resolve('src/index-v14.tsx'),publicDir:path.resolve('public')});
const browser=await openBrowser('chrome',{browserExecutable:exe});
const sceneSources=[96,300,500,585,795,950,1138,1280,1400,1460,1515,1602,1700,1760,1875,2043,2102];
try{for(const [locale,folder,label,id] of [['yue','yue','粵語','BOI-HK-Epic-v14'],['en','en','英文','BOI-HK-Epic-v14-EN'],['zh-CN','cn','簡中','BOI-HK-Epic-v14-CN']]){
 if(process.argv.some(a=>a.startsWith('--locale='))&&!process.argv.includes('--locale='+locale))continue;
 const t=JSON.parse(readFileSync('src/config/timeline-v14-'+folder+'.json','utf8')),old=t.oldTimeline;
 const oldToNew=f=>{const s=t.map.find(s=>f>=s.oldStart&&f<s.oldEnd)??t.map.find(s=>s.oldStart>=f)??t.map.at(-1);return s.newStart+Math.max(0,f-s.oldStart)*(s.newEnd-s.newStart)/(s.oldEnd-s.oldStart);};
 const sourceToNew=f=>{let a=f+old.sourceTimeline.holds.filter(h=>h.sourceFrame<=f).reduce((n,h)=>n+h.frames,0)+(f>=1652?old.peopleFrames:0);a-=old.redesignCuts.reduce((n,c)=>n+Math.min(c.frames,Math.max(0,a-c.startFrame)),0);return oldToNew(a);};
 const frames=[...new Set([...sceneSources.map(sourceToNew),...[0,6,12,18,24,36,48,60,75,110,150].map(f=>t.sceneStarts.platform+f),...[0,5,10,15,24,36,48,60,72].map(f=>t.sceneStarts.roots+f),...t.cues.map(c=>(c.startFrame+c.endFrame)/2)].map(Math.round).filter(f=>f>=0&&f<t.durationInFrames))].sort((a,b)=>a-b);
 const inputProps={locale,timeline:t,qa:true,muted:false},composition=await selectComposition({serveUrl:url,id,inputProps,browserExecutable:exe,puppeteerInstance:browser});
 const rows=[];const onBrowserLog=l=>{for(const prefix of ['FILM_V13_AUDIT:','PEOPLE_V13_AUDIT:']){let n=l.text.indexOf(prefix);if(n>=0)rows.push({frame:l.frame,kind:prefix,data:JSON.parse(l.text.slice(n+prefix.length))});}};
 if(!process.argv.includes('--render-only')){
  for(let i=0;i<frames.length;i+=4)await Promise.all(frames.slice(i,i+4).map(frame=>renderStill({serveUrl:url,composition,inputProps,frame,output:q+'/frames/'+folder+'-f'+frame+'.png',imageFormat:'png',browserExecutable:exe,puppeteerInstance:browser,onBrowserLog})));
  writeFileSync(q+'/'+folder+'-audit.json',JSON.stringify(rows,null,2));writeFileSync(q+'/'+folder+'-frame-index.json',JSON.stringify({frames,platformStart:t.sceneStarts.platform,rootsStart:t.sceneStarts.roots},null,2));console.log('STILLS READY',locale,frames.length);
 }
 if(!process.argv.includes('--stills-only')){
  const out='out/BOI-HK_史詩形象片_v14_'+label+'_節奏與同步精修版.mp4';if(existsSync(out))throw Error('Refuse overwrite '+out);
  let last=-1;await renderMedia({serveUrl:url,composition,inputProps:{...inputProps,qa:false},outputLocation:out,codec:'h264',crf:18,audioCodec:'aac',audioBitrate:'320k',pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:94,concurrency:6,browserExecutable:exe,puppeteerInstance:browser,onProgress:({progress})=>{let p=Math.floor(progress*10)*10;if(p!==last){last=p;console.log('RENDER',locale,p+'%');}}});console.log('DELIVERABLE',out);
 }
}}finally{await browser.close({silent:true});}
