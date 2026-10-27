import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import {writeFileSync,readFileSync,existsSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
const q='qa/us-v1-60s-v3',T=JSON.parse(readFileSync(`${q}/timeline.json`));
const browserExecutable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});
const browser=await openBrowser('chrome',{browserExecutable});
const audit=new Map();
const onBrowserLog=l=>{const i=l.text.indexOf('US_V3_AUDIT:');if(i>=0){const r=JSON.parse(l.text.slice(i+12));audit.set(r.frame,r);}};
const inputProps={qa:true,captions:true,primary:'en'};
try{
 const composition=await selectComposition({serveUrl,id:'US-Team-v1-60s-V3',inputProps,browserExecutable,puppeteerInstance:browser});
 const still=async(frame,output,props=inputProps,comp=composition)=>renderStill({serveUrl,composition:{...comp,props:{...comp.props,...props}},inputProps:props,frame,output,imageFormat:'png',browserExecutable,puppeteerInstance:browser,onBrowserLog});
 if(!process.argv.includes('--media-only')){
  for(const s of T.scenes){
   for(const [i,c] of s.subtitleCues.entries()){
    const from=s.voiceStartFrame+Math.ceil(s.words[c.startWord].start*30);
    const to=s.voiceStartFrame+Math.ceil(s.words[c.endWord].end*30);
    await still(Math.floor((from+to)/2),`${q}/frames/${s.id}-cue${i+1}.png`);
   }
  }
  for(const sec of [.6,1.25,2,2.6,3.2,3.94,4.2]) await still(1583+Math.ceil(sec*30),`${q}/logo-growth-frames/local-${sec.toFixed(2)}s.png`,{...inputProps,captions:false});
  await still(1799,`${q}/frames/final-logo.png`,{...inputProps,captions:false});
  await still(483,`${q}/frames/team-no-captions-f120.png`,{...inputProps,captions:false});
  const v2=await selectComposition({serveUrl,id:'US-Team-v1-60s-V2',inputProps:{qa:false},browserExecutable,puppeteerInstance:browser});
  await still(483,`${q}/frames/team-v2-f120.png`,{qa:false},v2);
  const reference=await selectComposition({serveUrl,id:'BOI-HK-Official-Reference-v10',browserExecutable,puppeteerInstance:browser});
  await still(0,`${q}/frames/official-reference.png`,{},reference);
  console.log('V3 caption and growth stills saved');
 }
 if(!process.argv.includes('--stills-only')){
  for(const captions of (process.argv.includes('--clean-only') ? [false] : [true,false])){
   const props={...inputProps,qa:captions,captions};
   const video=`${q}/video-${captions?'bilingual':'clean'}.mp4`;
   const output=`out/US-Team-v1_60s_雙語字幕版${captions?'':'_無字幕'}.mp4`;
   if(existsSync(video)||existsSync(output))throw Error(`Refuse overwrite ${output}`);
   let last=-1; audit.clear();
   await renderMedia({serveUrl,composition:{...composition,props:{...composition.props,...props}},inputProps:props,outputLocation:video,codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:96,concurrency:4,muted:true,browserExecutable,puppeteerInstance:browser,onBrowserLog,onProgress:({progress})=>{const p=Math.floor(progress*10);if(p!==last){last=p;console.log(captions?'Bilingual':'Clean',p*10+'%');}}});
   if(captions)writeFileSync(`${q}/frame-audit.json`,JSON.stringify(Object.fromEntries([...audit].sort((a,b)=>a[0]-b[0])),null,2));
   // Copy the original V2 AAC stream byte-for-byte: no re-encoding or timing changes.
   execFileSync('ffmpeg',['-v','error','-i',video,'-i','out/US-Team-v1_60s_內容版.mp4','-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',output]);
   console.log('Saved',output);
  }
 }
}finally{await browser.close({silent:true});}
