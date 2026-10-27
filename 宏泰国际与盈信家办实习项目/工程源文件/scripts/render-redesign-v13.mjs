import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderMedia,renderStill} from '@remotion/renderer';
import {existsSync,mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';import {fileURLToPath} from 'node:url';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'));
const preview=process.argv.includes('--yue-preview');
const t=JSON.parse(readFileSync(preview?'src/config/timeline-v13-preview.json':'src/config/timeline-v13-redesign.json','utf8'));
const q=preview?'qa/v13/full/yue-preview-r01':'qa/v13/redesign',exe='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';mkdirSync(`${q}/frames`,{recursive:true});
const url=await bundle({entryPoint:path.resolve('src/index-v13-redesign.tsx'),publicDir:path.resolve('public')});
const browser=await openBrowser('chrome',{browserExecutable:exe});
const old=t.sourceTimeline; const originalToFinal=f=>{const x=f+old.holds.filter(h=>h.sourceFrame<=f).reduce((s,h)=>s+h.frames,0)+(f>=1652?t.peopleFrames:0);return x-t.redesignCuts.reduce((n,c)=>n+Math.min(c.frames,Math.max(0,x-c.startFrame)),0);};
let p=t.peopleStartFrame+t.peoplePlan.openingFrames;
const peopleFrames=t.peoplePlan.personFrames.flatMap(n=>{const result=[p+12,p+33];p+=n;return result;});
peopleFrames.push(p+t.peoplePlan.returnFrames+t.peoplePlan.exitFrames+30);
const frames=[...new Set([96,300,439,470,500,518,534,550,585,605,660,712,735,795,860,875,950,1050,1138,1150,1190,1280,1320,1358,1400,1460,1515,1550,1602,1662,1700,1760,1805,1875,2043,2102].map(originalToFinal).concat(peopleFrames,Array.from({length:8},(_,i)=>t.peopleStartFrame+t.peoplePlan.openingFrames+6+i*2)))].sort((a,b)=>a-b);
const versions=preview?[['yue','BOI-HK-Epic-v13','粵語']]:[['yue','BOI-HK-Epic-v13','粵語'],['en','BOI-HK-Epic-v13-EN','英文'],['zh-CN','BOI-HK-Epic-v13-CN','簡中']];
try{for(const [locale,id,label] of versions){
 if(process.argv.some(x=>x.startsWith('--locale='))&&!process.argv.includes(`--locale=${locale}`))continue;
 const inputProps={locale,timeline:t,qa:true,muted:false,audioFolder:preview?'hk-v13-preview':'hk-v13-redesign'};
 const composition=await selectComposition({serveUrl:url,id,inputProps,browserExecutable:exe,puppeteerInstance:browser});
 const rows=[];const onBrowserLog=l=>{for(const prefix of ['FILM_V13_AUDIT:','PEOPLE_V13_AUDIT:']){const i=l.text.indexOf(prefix);if(i>=0)rows.push({kind:prefix,data:JSON.parse(l.text.slice(i+prefix.length))});}};
 if(!process.argv.includes('--render-only')){
  for(let i=0;i<frames.length;i+=4)await Promise.all(frames.slice(i,i+4).map(frame=>{const output=`${q}/frames/${locale}-f${frame}.png`;if(existsSync(output))return;return renderStill({serveUrl:url,composition,inputProps,frame,output,imageFormat:'png',browserExecutable:exe,puppeteerInstance:browser,onBrowserLog});}));
  writeFileSync(`${q}/${locale}-layout-audit.json`,JSON.stringify(rows,null,2));console.log('STILLS READY',locale,frames.length);
 }
 if(!process.argv.includes('--stills-only')){
  const output=`out/BOI-HK_史詩形象片_v13_${label}_${preview?'加長預覽_r01':'重設計版'}.mp4`;if(existsSync(output))throw Error('Refuse overwrite '+output);
  let last=-1;await renderMedia({serveUrl:url,composition,inputProps:{...inputProps,qa:false},outputLocation:output,codec:'h264',crf:18,audioCodec:'aac',audioBitrate:'320k',pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:94,concurrency:10,browserExecutable:exe,puppeteerInstance:browser,onProgress:({progress})=>{let pct=Math.floor(progress*20)*5;if(pct!==last){last=pct;console.log('RENDER',locale,pct+'%');}}});console.log('DELIVERABLE',output);
 }
}}finally{await browser.close({silent:true});}
