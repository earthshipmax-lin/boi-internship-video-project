import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderMedia,renderStill} from '@remotion/renderer';
import {existsSync,mkdirSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'));
const q='qa/v13/people/visual-study-r04',exe='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
mkdirSync(`${q}/frames`,{recursive:true});
const serveUrl=await bundle({entryPoint:path.resolve('qa/v13/people/visual-study-entry.tsx'),publicDir:path.resolve('public')});
const browser=await openBrowser('chrome',{browserExecutable:exe});
const frames=[30,...Array.from({length:6},(_,i)=>[60+72*i+12,60+72*i+27,60+72*i+60]).flat(),500,540,602,...Array.from({length:8},(_,i)=>142+i)].sort((a,b)=>a-b);
try{
 for(const locale of ['yue','en','zh-CN']){
  const rows=new Map(),prefix='PEOPLE_V13_AUDIT:';
  const onBrowserLog=l=>{const i=l.text.indexOf(prefix);if(i>=0){const r=JSON.parse(l.text.slice(i+prefix.length));rows.set(r.frame,r);}};
  const save=kind=>writeFileSync(`${q}/${locale}-${kind}.json`,JSON.stringify(Object.fromEntries([...rows].sort((a,b)=>a[0]-b[0])),null,2)+'\n');
  const inputProps={locale,qa:true};
  const composition=await selectComposition({serveUrl,id:'HK-People-v13-VisualStudy',inputProps,browserExecutable:exe,puppeteerInstance:browser});
  if(!process.argv.includes('--render-only')){
   for(let i=0;i<frames.length;i+=4)await Promise.all(frames.slice(i,i+4).map(frame=>{
    const output=`${q}/frames/${locale}-f${frame}.png`;if(existsSync(output))throw Error('Refuse overwrite '+output);
    return renderStill({serveUrl,composition,inputProps,frame,output,imageFormat:'png',browserExecutable:exe,puppeteerInstance:browser,onBrowserLog});
   }));
   save('stills');console.log('People stills',locale,frames.length);
  }
  if(!process.argv.includes('--stills-only')){
   rows.clear();const output=locale==='yue'?'out/BOI-HK_v13_人物手風琴_畫面試片_無配音.mp4':`${q}/${locale}-silent-study.mp4`;
   if(existsSync(output))throw Error('Refuse overwrite '+output);
   let last=-1;
   await renderMedia({serveUrl,composition,inputProps,outputLocation:output,codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:94,concurrency:4,muted:true,browserExecutable:exe,puppeteerInstance:browser,onBrowserLog,onProgress:({progress})=>{const p=Math.floor(progress*4);if(p!==last){last=p;console.log('People render',locale,p*25+'%');}}});
   save('all-frames');console.log('SILENT VISUAL STUDY',locale,output);
  }
 }
}finally{await browser.close({silent:true});}
