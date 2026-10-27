import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import {writeFileSync,readFileSync,existsSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
const q='qa/us-v1-60s-v2',inputProps={qa:true},T=JSON.parse(readFileSync(`${q}/timeline.json`));
const browserExecutable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});const browser=await openBrowser('chrome',{browserExecutable});const audit=new Map();
const onBrowserLog=l=>{const i=l.text.indexOf('US_V2_AUDIT:');if(i>=0){const r=JSON.parse(l.text.slice(i+12));audit.set(r.frame,r);}};
try{
 const composition=await selectComposition({serveUrl,id:'US-Team-v1-60s-V2',inputProps,browserExecutable,puppeteerInstance:browser});
 for(const s of T.scenes){const duration=s.endFrame-s.startFrame;const local=['S3','S4','S7'].includes(s.id)?duration-30:Math.round(duration*.7);await renderStill({serveUrl,composition,inputProps,frame:s.startFrame+local,output:`${q}/frames/${s.id}.png`,imageFormat:'png',browserExecutable,puppeteerInstance:browser,onBrowserLog});}
 const team=T.scenes.find(s=>s.id==='S2');
 await renderStill({serveUrl,composition,inputProps,frame:team.startFrame+120,output:`${q}/frames/team-full-f120.png`,imageFormat:'png',browserExecutable,puppeteerInstance:browser});
 const reference=await selectComposition({serveUrl,id:'US-Team-v1',browserExecutable,puppeteerInstance:browser});
 await renderStill({serveUrl,composition:reference,frame:120,output:`${q}/frames/team-reference-f120.png`,imageFormat:'png',browserExecutable,puppeteerInstance:browser});
 if(process.argv.includes('--stills-only'))console.log('Stills saved');else {
 const video=`${q}/video-only.mp4`,output='out/US-Team-v1_60s_內容版.mp4';if(existsSync(video)||existsSync(output))throw Error('Refuse overwrite');let last=-1;audit.clear();
 await renderMedia({serveUrl,composition,inputProps,outputLocation:video,codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:96,concurrency:4,muted:true,browserExecutable,puppeteerInstance:browser,onBrowserLog,onProgress:({progress})=>{const p=Math.floor(progress*10);if(p!==last){last=p;console.log('Render V2',p*10+'%');}}});
 writeFileSync(`${q}/frame-audit.json`,JSON.stringify(Object.fromEntries([...audit].sort((a,b)=>a[0]-b[0])),null,2));
 execFileSync('ffmpeg',['-v','error','-i',video,'-i','public/music/us-v2/full-review-mix.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-movflags','+faststart',output]);console.log('Saved',output);
 }
}finally{await browser.close({silent:true});}
