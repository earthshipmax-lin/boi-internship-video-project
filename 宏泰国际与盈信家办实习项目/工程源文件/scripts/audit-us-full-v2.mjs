import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderFrames} from '@remotion/renderer';
import {writeFileSync} from 'node:fs';
import path from 'node:path';
const q='qa/us-v1-60s-v2',inputProps={qa:true};
const browserExecutable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});const browser=await openBrowser('chrome',{browserExecutable});const audit=new Map();
const onBrowserLog=l=>{const i=l.text.indexOf('US_V2_AUDIT:');if(i>=0){const r=JSON.parse(l.text.slice(i+12));audit.set(r.frame,r);}};
try{
 const composition=await selectComposition({serveUrl,id:'US-Team-v1-60s-V2',inputProps,browserExecutable,puppeteerInstance:browser});let last=-1;
 await renderFrames({serveUrl,composition,inputProps,outputDir:null,onFrameBuffer:()=>{},imageFormat:'jpeg',jpegQuality:40,scale:1,concurrency:4,muted:true,browserExecutable,puppeteerInstance:browser,onBrowserLog,onStart:()=>{},onFrameUpdate:n=>{const p=Math.floor(n/composition.durationInFrames*4);if(p!==last){last=p;console.log('Audit',p*25+'%');}}});
 writeFileSync(`${q}/frame-audit.json`,JSON.stringify(Object.fromEntries([...audit].sort((a,b)=>a[0]-b[0])),null,2));console.log('Audit complete',audit.size);
}finally{await browser.close({silent:true});}
