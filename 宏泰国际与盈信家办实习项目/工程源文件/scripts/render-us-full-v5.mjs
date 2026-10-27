import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import {writeFileSync,existsSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
const q='qa/us-v1-60s-v5',browserExecutable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const inputProps={qa:true,captions:true,primary:'en'};
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});
const browser=await openBrowser('chrome',{browserExecutable});const audit=new Map();
const onBrowserLog=l=>{const i=l.text.indexOf('US_V5_AUDIT:');if(i>=0){const a=JSON.parse(l.text.slice(i+12));audit.set(a.frame,a);}};
try{
 const composition=await selectComposition({serveUrl,id:'US-Team-v1-60s-V5',inputProps,browserExecutable,puppeteerInstance:browser});
 const still=async(frame,file,comp=composition,props=inputProps)=>renderStill({serveUrl,composition:{...comp,props:{...comp.props,...props}},inputProps:props,frame,output:`${q}/${file}.png`,imageFormat:'png',browserExecutable,puppeteerInstance:browser,onBrowserLog});
 if(!process.argv.includes('--media-only')){
  for(const seconds of [0,.5,1,1.6])await still(120+Math.ceil(seconds*30),`s1-logo-frames/local-${seconds.toFixed(1)}s`);
  for(const [i,frame] of [44,80,116,152,188,218].entries())await still(363+frame,`s2-focus-frames/person-${i+1}`);
  for(const frame of [363,374,375,376,390,410,411,412,414,420,447,483,519,555,584,585,595,602])await still(frame,`frames/team-f${frame}`);
  const old=await selectComposition({serveUrl,id:'US-Team-v1-60s-V4',inputProps:{qa:false},browserExecutable,puppeteerInstance:browser});
  for(const frame of [0,50,119,603,640,762,876,907,1050,1110,1139,1417,1492,1493,1529,1582,1583,1709,1799]){
   await still(frame,`frames/preserved-v5-f${frame}`);await still(frame,`frames/preserved-v4-f${frame}`,old,{qa:false,captions:true,primary:'en'});
  }
  await still(324,'frames/S1-v5');await still(483,'frames/S2-v5');
  writeFileSync(`${q}/stills-audit.json`,JSON.stringify(Object.fromEntries(audit),null,2));console.log('V5 stills saved');
 }
 if(!process.argv.includes('--stills-only')){
  const video=`${q}/video-only.mp4`,output='out/US-Team-v1_60s_配樂與人物版.mp4';
  if(existsSync(video)||existsSync(output))throw Error('Refuse overwrite V5');audit.clear();let last=-1;
  await renderMedia({serveUrl,composition,inputProps,outputLocation:video,codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:96,concurrency:4,muted:true,browserExecutable,puppeteerInstance:browser,onBrowserLog,onProgress:({progress})=>{const p=Math.floor(progress*10);if(p!==last){last=p;console.log('V5 render',p*10+'%');}}});
  writeFileSync(`${q}/frame-audit.json`,JSON.stringify(Object.fromEntries([...audit].sort((a,b)=>a[0]-b[0])),null,2));
  execFileSync('ffmpeg',['-v','error','-i',video,'-i','public/music/us-v2/full-review-mix-v5.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-movflags','+faststart',output]);console.log('Saved',output);
 }
}finally{await browser.close({silent:true});}
