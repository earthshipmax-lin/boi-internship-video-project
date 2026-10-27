import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import {existsSync,mkdirSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'));
const qa='qa/v11/film';mkdirSync(qa,{recursive:true});
const browserExecutable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});
const browser=await openBrowser('chrome',{browserExecutable});
try{
 const composition=await selectComposition({serveUrl,id:'BOI-HK-Epic-v11',browserExecutable,puppeteerInstance:browser});
 if(!process.argv.includes('--render-only')){
  const times=[3.5,9,15.7,18.9,21.7,25.5,32.5,40.5,45.5,50.5,56.5,64.5,66,67.5,67.96666666666667];
  for(const t of times){await renderStill({serveUrl,composition,frame:Math.round(t*30),output:`${qa}/still-${String(t).replace('.','_')}.png`,browserExecutable,puppeteerInstance:browser,imageFormat:'png'});console.log('QA',t);}
 }
 if(!process.argv.includes('--stills-only')){
  const outputLocation='out/BOI-HK_史詩形象片_v11.mp4';
  if(existsSync(outputLocation))throw new Error('Output exists; refusing overwrite');
  let previous=-1;
  await renderMedia({serveUrl,composition,outputLocation,codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:94,concurrency:4,browserExecutable,puppeteerInstance:browser,audioCodec:'aac',audioBitrate:'320k',onProgress:({progress})=>{const step=Math.floor(progress*20);if(step!==previous){previous=step;console.log('Rendering',step*5+'%');}}});
  console.log('FINAL',outputLocation,composition.durationInFrames,'frames');
 }
}finally{await browser.close({silent:true});}
