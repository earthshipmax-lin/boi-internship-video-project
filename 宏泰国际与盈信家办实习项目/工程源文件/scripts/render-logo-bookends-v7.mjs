import {bundle} from '@remotion/bundler';
import {selectComposition,renderStill,renderMedia,openBrowser} from '@remotion/renderer';
import {mkdirSync,readFileSync,writeFileSync,existsSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'));
const qa='qa/v7';mkdirSync(`${qa}/parts`,{recursive:true});
const browserExecutable=process.env.BOI_CHROME??'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});
const browser=await openBrowser('chrome',{browserExecutable});
const picks={intro:[0,18,36,66,96,108,132,149],outro:[0,18,36,66,96,108,132,165,195]};
const frames={};
try{
 for(const [name,id] of [['intro','BOI-HK-Intro-v7'],['outro','BOI-HK-Outro-v7']]){
  const composition=await selectComposition({serveUrl,id,browserExecutable,puppeteerInstance:browser});
  for(const frame of picks[name]){
   const output=`${qa}/${name}-f${String(frame).padStart(3,'0')}.png`;
   await renderStill({serveUrl,composition,frame,output,browserExecutable,puppeteerInstance:browser,imageFormat:'png'});
   frames[`${name}-${frame}`]={file:output,frame,time:frame/30};
  }
  const outputLocation=`${qa}/parts/${name}-native.mp4`;
  if(existsSync(outputLocation))throw new Error(`Refusing to overwrite ${outputLocation}`);
  await renderMedia({serveUrl,composition,outputLocation,codec:'h264',crf:14,pixelFormat:'yuv420p',
   imageFormat:'png',muted:true,concurrency:4,browserExecutable,puppeteerInstance:browser,
   onProgress:({progress})=>{if(progress===1)console.log(name,'rendered');}});
  console.log(name,composition.durationInFrames,'frames');
 }
 writeFileSync(`${qa}/keyframes.json`,JSON.stringify(frames,null,2));
}finally{await browser.close({silent:true});}
