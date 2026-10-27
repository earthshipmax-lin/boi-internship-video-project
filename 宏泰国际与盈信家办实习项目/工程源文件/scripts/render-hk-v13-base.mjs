import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderMedia,renderStill} from '@remotion/renderer';
import {existsSync,mkdirSync,writeFileSync} from 'node:fs';
import path from 'node:path';import {fileURLToPath} from 'node:url';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'));
const revision=process.argv.find(x=>x.startsWith('--revision='))?.split('=')[1]??'r01';
const q=`qa/v13/full/base-${revision}`,exe='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
mkdirSync(`${q}/frames`,{recursive:true});
const serveUrl=await bundle({entryPoint:path.resolve('qa/v13/full/base-entry.tsx'),publicDir:path.resolve('public')});
const browser=await openBrowser('chrome',{browserExecutable:exe});
const frames=[96,300,500,570,660,750,810,900,948,1038,1071,1140,1210,1280,1326,1358,1400,1460,1515,1550,1602,1700,1875,2043,2102];
try{
 for(const locale of ['yue','en','zh-CN']){
  const rows=new Map(),prefix='FILM_V13_AUDIT:';
  const onBrowserLog=l=>{const i=l.text.indexOf(prefix);if(i>=0){const r=JSON.parse(l.text.slice(i+prefix.length));rows.set(r.sourceFrame,r);}};
  const save=kind=>writeFileSync(`${q}/${locale}-${kind}.json`,JSON.stringify(Object.fromEntries([...rows].sort((a,b)=>a[0]-b[0])),null,2)+'\n');
  const inputProps={locale,qa:true};
  const composition=await selectComposition({serveUrl,id:'HK-V13-BasePicture',inputProps,browserExecutable:exe,puppeteerInstance:browser});
  if(!process.argv.includes('--render-only')){
   for(let i=0;i<frames.length;i+=4)await Promise.all(frames.slice(i,i+4).map(frame=>{const output=`${q}/frames/${locale}-f${frame}.png`;if(existsSync(output))throw Error('Refuse overwrite '+output);return renderStill({serveUrl,composition,inputProps,frame,output,imageFormat:'png',browserExecutable:exe,puppeteerInstance:browser,onBrowserLog});}));
   save('stills');console.log('BASE STILLS',locale,rows.size);
  }
  if(!process.argv.includes('--stills-only')){
   rows.clear();const output=`${q}/${locale}-base-picture.mp4`;if(existsSync(output))throw Error('Refuse overwrite '+output);
   let last=-1;await renderMedia({serveUrl,composition,inputProps,outputLocation:output,codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:94,concurrency:4,muted:true,browserExecutable:exe,puppeteerInstance:browser,onBrowserLog,onProgress:({progress})=>{const p=Math.floor(progress*4);if(p!==last){last=p;console.log('BASE RENDER',locale,p*25+'%');}}});save('all-frames');console.log('BASE DONE',locale,output);
  }
 }
 if(!process.argv.includes('--render-only')){
  const composition=await selectComposition({serveUrl,id:'HK-V13-Background',browserExecutable:exe,puppeteerInstance:browser});const output=`${q}/background.png`;if(existsSync(output))throw Error('Refuse overwrite '+output);await renderStill({serveUrl,composition,frame:0,output,imageFormat:'png',browserExecutable:exe,puppeteerInstance:browser});
 }
}finally{await browser.close({silent:true});}
