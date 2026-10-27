import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import {existsSync,mkdirSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'));
const qa='qa/v12';mkdirSync(qa,{recursive:true});
const browserExecutable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});
const browser=await openBrowser('chrome',{browserExecutable});
try{
 const composition=await selectComposition({serveUrl,id:'BOI-HK-Epic-v12-Stage1',browserExecutable,puppeteerInstance:browser});
 if(!process.argv.includes('--render-only')){
  for(const t of (process.argv.includes('--fix-stills')?[26.5,34.5]:[3.5,15.7,18.9,24.2,26.5,28.0,30.4,31.26,31.6,32.03,32.2,32.4,32.9,33.4,33.46,33.8,34.5,40.5,62.3,66,67.9666666667])){
   await renderStill({serveUrl,composition,frame:Math.round(t*30),output:`${qa}/still-${t.toFixed(2)}.png`,browserExecutable,puppeteerInstance:browser,imageFormat:'png'});
  }
  console.log('V12 QA stills ready');
 }
 if(!process.argv.includes('--stills-only')){
  const outputLocation='out/BOI-HK_史詩形象片_v12_第一階段試片.mp4';
  if(existsSync(outputLocation))throw new Error('Output exists; refusing overwrite');
  let last=-1;
  await renderMedia({serveUrl,composition,outputLocation,codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:94,concurrency:4,browserExecutable,puppeteerInstance:browser,audioCodec:'aac',audioBitrate:'320k',onProgress:({progress})=>{const p=Math.floor(progress*10);if(p!==last){last=p;console.log('Rendering',p*10+'%');}}});
  console.log('FINAL',outputLocation);
 }
}finally{await browser.close({silent:true});}
