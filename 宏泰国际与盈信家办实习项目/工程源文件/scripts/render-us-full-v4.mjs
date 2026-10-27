import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import {writeFileSync,readFileSync,existsSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
const q='qa/us-v1-60s-v4';
const browserExecutable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});
const browser=await openBrowser('chrome',{browserExecutable});
const inputProps={qa:true,captions:true,primary:'en'};
const audit=new Map();
const onBrowserLog=log=>{const i=log.text.indexOf('US_V4_AUDIT:');if(i>=0){const record=JSON.parse(log.text.slice(i+12));audit.set(record.frame,record);}};
try{
 const composition=await selectComposition({serveUrl,id:'US-Team-v1-60s-V4',inputProps,browserExecutable,puppeteerInstance:browser});
 if(!process.argv.includes('--media-only')){
  const old=await selectComposition({serveUrl,id:'US-Team-v1-60s-V3',inputProps:{qa:false,captions:true,primary:'en'},browserExecutable,puppeteerInstance:browser});
  const still=async(frame,file,comp=composition,props=inputProps)=>renderStill({serveUrl,composition:{...comp,props:{...comp.props,...props}},inputProps:props,frame,output:`${q}/frames/${file}.png`,imageFormat:'png',browserExecutable,puppeteerInstance:browser,onBrowserLog});
  for(const [scene,frame] of [['S1',324],['S3',876],['S4',1110],['S5',1450]]){
   await still(frame,`${scene}-v4`);await still(frame,`${scene}-v3`,old,{qa:false,captions:true,primary:'en'});
  }
  for(const frame of [0,6,50,119,363,483,602,1493,1529,1582,1583,1640,1709,1799]){
   await still(frame,`preserved-v4-f${frame}`);await still(frame,`preserved-v3-f${frame}`,old,{qa:false,captions:true,primary:'en'});
  }
  // Sample each cue once so the changing visual content is reviewed with its captions.
  const T=JSON.parse(readFileSync(`${q}/timeline.json`));
  for(const s of T.scenes.filter(s=>['S1','S3','S4','S5'].includes(s.id))){
   for(const [i,c] of s.subtitleCues.entries()){
    const frame=s.voiceStartFrame+Math.ceil((s.words[c.startWord].start+s.words[c.endWord].end)*15);
    await still(frame,`${s.id}-cue${i+1}`);
   }
  }
  writeFileSync(`${q}/stills-audit.json`,JSON.stringify(Object.fromEntries(audit),null,2));
  console.log('V4 stills and V3 comparisons saved');
 }
 if(!process.argv.includes('--stills-only')){
  const video=`${q}/video-only.mp4`,output='out/US-Team-v1_60s_證據版.mp4';
  if(existsSync(video)||existsSync(output))throw Error('Refuse overwrite existing V4');
  audit.clear();let last=-1;
  await renderMedia({serveUrl,composition,inputProps,outputLocation:video,codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:96,concurrency:4,muted:true,browserExecutable,puppeteerInstance:browser,onBrowserLog,onProgress:({progress})=>{const p=Math.floor(progress*10);if(p!==last){last=p;console.log('V4 render',p*10+'%');}}});
  writeFileSync(`${q}/frame-audit.json`,JSON.stringify(Object.fromEntries([...audit].sort((a,b)=>a[0]-b[0])),null,2));
  execFileSync('ffmpeg',['-v','error','-i',video,'-i','out/US-Team-v1_60s_雙語字幕版.mp4','-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',output]);
  console.log('Saved',output);
 }
}finally{await browser.close({silent:true});}
