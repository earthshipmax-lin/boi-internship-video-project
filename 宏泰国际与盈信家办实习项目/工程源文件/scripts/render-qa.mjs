import {bundle} from '@remotion/bundler';
import {selectComposition,renderStill,openBrowser} from '@remotion/renderer';
import {mkdirSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'));
const root=process.cwd();mkdirSync('qa/v2',{recursive:true});
const browserExecutable=process.env.BOI_CHROME??'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});
const browser=await openBrowser('chrome',{browserExecutable});
try{
 const composition=await selectComposition({serveUrl,id:'BOI-HK-Natural-v2',browserExecutable,puppeteerInstance:browser});
 const picks=JSON.parse((await import('node:fs')).readFileSync('qa/v2/qa-picks.json','utf8'));
 for(const [id,frame] of picks){await renderStill({serveUrl,composition,frame,output:`qa/v2/${id}.png`,browserExecutable,puppeteerInstance:browser,imageFormat:'png'});console.log('QA',id,frame);}
 const logo=await selectComposition({serveUrl,id:'BOI-HK-Logo-Hold',browserExecutable,puppeteerInstance:browser});
 for(const frame of [114,150,252,285]){await renderStill({serveUrl,composition:logo,frame,output:`qa/v2/S0-${frame}.png`,browserExecutable,puppeteerInstance:browser,imageFormat:'png'});}
 const reference=await selectComposition({serveUrl,id:'BOI-HK-Prototype-Reference',browserExecutable,puppeteerInstance:browser});
 for(const frame of [114,150,252,285]) await renderStill({serveUrl,composition:reference,frame,output:`qa/v2/prototype-f${frame}.png`,browserExecutable,puppeteerInstance:browser,imageFormat:'png'});
 writeFileSync('qa/v2/keyframes.json',JSON.stringify(Object.fromEntries(picks),null,2));
}finally{await browser.close({silent:true});}
