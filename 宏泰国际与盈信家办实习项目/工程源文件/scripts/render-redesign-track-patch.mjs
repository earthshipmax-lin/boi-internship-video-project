import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderMedia} from '@remotion/renderer';
import {readFileSync,mkdirSync,existsSync} from 'node:fs';
import path from 'node:path';
const t=JSON.parse(readFileSync('src/config/timeline-v13-redesign.json','utf8')),old=t.sourceTimeline;
const map=f=>{let n=f+old.holds.filter(h=>h.sourceFrame<=f).reduce((a,h)=>a+h.frames,0);return n-t.redesignCuts.reduce((a,c)=>a+Math.min(c.frames,Math.max(0,n-c.startFrame)),0);};
const range=[map(431),map(618)-1],q='qa/v13/redesign/track-patch';mkdirSync(q,{recursive:true});
const exe='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',url=await bundle({entryPoint:path.resolve('src/index-v13-redesign.tsx'),publicDir:path.resolve('public')}),browser=await openBrowser('chrome',{browserExecutable:exe});
try{for(const [locale,id] of [['yue','BOI-HK-Epic-v13'],['en','BOI-HK-Epic-v13-EN'],['zh-CN','BOI-HK-Epic-v13-CN']]){
 const inputProps={locale,timeline:t,qa:false,muted:true},composition=await selectComposition({serveUrl:url,id,inputProps,browserExecutable:exe,puppeteerInstance:browser});
 const output=q+'/'+locale+'.mp4';if(existsSync(output))throw Error('Refuse overwrite');
 await renderMedia({serveUrl:url,composition,inputProps,outputLocation:output,frameRange:range,codec:'h264',crf:16,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:96,concurrency:4,browserExecutable:exe,puppeteerInstance:browser});console.log('TRACK PATCH',locale,range);
}}finally{await browser.close({silent:true});}
