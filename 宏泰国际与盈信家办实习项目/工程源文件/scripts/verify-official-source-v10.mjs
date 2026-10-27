import {bundle} from '@remotion/bundler';
import {selectComposition,renderStill,openBrowser} from '@remotion/renderer';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'));
const browserExecutable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});
const browser=await openBrowser('chrome',{browserExecutable});
try{
 const composition=await selectComposition({serveUrl,id:'BOI-HK-Official-Reference-v10',browserExecutable,puppeteerInstance:browser});
 await renderStill({serveUrl,composition,frame:0,output:'qa/v10/official-reference-native.png',browserExecutable,puppeteerInstance:browser,imageFormat:'png'});
}finally{await browser.close({silent:true});}
