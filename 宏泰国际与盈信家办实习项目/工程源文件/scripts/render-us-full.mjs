import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import {writeFileSync,readFileSync,existsSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
const q='qa/us-v1-60s',inputProps={qa:true},T=JSON.parse(readFileSync(`${q}/timeline.json`));
const browserExecutable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});const browser=await openBrowser('chrome',{browserExecutable});const audit=new Map();
const onBrowserLog=l=>{const i=l.text.indexOf('US_FULL_AUDIT:');if(i>=0){const r=JSON.parse(l.text.slice(i+14));audit.set(r.frame,r);}};
try{
 const composition=await selectComposition({serveUrl,id:'US-Team-v1-60s',inputProps,browserExecutable,puppeteerInstance:browser});
 for(const s of T.scenes)await renderStill({serveUrl,composition,inputProps,frame:s.startFrame+Math.min(s.endFrame-s.startFrame-20,s.id==='S6'?240:Math.round((s.endFrame-s.startFrame)*.7)),output:`${q}/frames/${s.id}.png`,imageFormat:'png',browserExecutable,puppeteerInstance:browser});
 const team=T.scenes.find(s=>s.id==='S2');
 await renderStill({serveUrl,composition,inputProps,frame:team.startFrame+120,output:`${q}/frames/team-full-f120.png`,imageFormat:'png',browserExecutable,puppeteerInstance:browser});
 const reference=await selectComposition({serveUrl,id:'US-Team-v1',browserExecutable,puppeteerInstance:browser});
 await renderStill({serveUrl,composition:reference,frame:120,output:`${q}/frames/team-reference-f120.png`,imageFormat:'png',browserExecutable,puppeteerInstance:browser});
 if(process.argv.includes('--stills-only')){console.log('Stills saved');} else {
 const video=`${q}/video-only.mp4`,output='out/US-Team-v1_60s_初版.mp4';if(existsSync(video)||existsSync(output))throw Error('Refuse overwrite');let last=-1;
 await renderMedia({serveUrl,composition,inputProps,outputLocation:video,codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:96,concurrency:4,muted:true,browserExecutable,puppeteerInstance:browser,onBrowserLog,onProgress:({progress})=>{const p=Math.floor(progress*10);if(p!==last){last=p;console.log('Render',p*10+'%');}}});
 writeFileSync(`${q}/frame-audit.json`,JSON.stringify(Object.fromEntries([...audit].sort((a,b)=>a[0]-b[0])),null,2));
 execFileSync('ffmpeg',['-v','error','-i',video,'-i','public/music/us-v1/full-review-mix.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-movflags','+faststart',output]);console.log('Saved',output);
 }
}finally{await browser.close({silent:true});}
