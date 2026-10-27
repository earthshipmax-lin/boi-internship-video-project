import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import {mkdirSync,writeFileSync,existsSync} from 'node:fs';
import path from 'node:path';
const q='qa/us-v1';mkdirSync(`${q}/frames`,{recursive:true});
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});
const browserExecutable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const browser=await openBrowser('chrome',{browserExecutable});
const audit=new Map();const inputProps={qa:true};
const onBrowserLog=log=>{const i=log.text.indexOf('US_AUDIT:');if(i>=0){const a=JSON.parse(log.text.slice(i+9));audit.set(a.frame,a);}};
try{
 const composition=await selectComposition({serveUrl,id:'US-Team-v1',inputProps,browserExecutable,puppeteerInstance:browser});
 for(const frame of [0,3,6,9,12,15,26,32,60,120,210,230,234,239])await renderStill({serveUrl,composition,inputProps,frame,output:`${q}/frames/f${frame}.png`,imageFormat:'png',browserExecutable,puppeteerInstance:browser,onBrowserLog});
 await renderStill({serveUrl,composition,inputProps,frame:120,output:'out/US-Team-v1-still.png',imageFormat:'png',browserExecutable,puppeteerInstance:browser});
 const output='out/US-Team-v1-visual-study.mp4';if(existsSync(output))throw Error('Refuse overwrite '+output);
 await renderMedia({serveUrl,composition,inputProps,outputLocation:output,codec:'h264',crf:16,pixelFormat:'yuv420p',imageFormat:'png',concurrency:4,muted:true,browserExecutable,puppeteerInstance:browser,onBrowserLog,onProgress:({progress})=>{if(Math.round(progress*100)%25===0)console.log('Render',Math.round(progress*100)+'%');}});
 writeFileSync(`${q}/frame-audit.json`,JSON.stringify(Object.fromEntries([...audit].sort((a,b)=>a[0]-b[0])),null,2));
 console.log('Saved 8s visual study and still; silent while voice selection pending.');
}finally{await browser.close({silent:true});}
