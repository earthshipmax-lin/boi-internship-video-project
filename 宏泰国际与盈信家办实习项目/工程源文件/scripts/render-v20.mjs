import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderMedia,renderStill} from '@remotion/renderer';
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import path from 'node:path';
const q='qa/v20',exe='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';mkdirSync(q+'/frames',{recursive:true});
const url=await bundle({entryPoint:path.resolve('src/index-v20.tsx'),publicDir:path.resolve('public')}),browser=await openBrowser('chrome',{browserExecutable:exe});
try{for(const [loc,id] of [['cn','CN'],['yue','YUE'],['en','EN']]){
 const t=JSON.parse(readFileSync(`src/config/timeline-v20-${loc}.json`)),props={timeline:t,qa:false,muted:true},opts={serveUrl:url,id:'BOI-HK-Epic-v20-'+id,browserExecutable:exe,puppeteerInstance:browser};
 const comp=await selectComposition({...opts,inputProps:props});
 const rows=[];for(const f of [t.edit.fadeStart+4,t.edit.rootsStart-1,t.edit.rootsStart+7,t.edit.rootsStart+23,t.edit.rootsStart+40,t.durationInFrames-65])await renderStill({...opts,composition:comp,inputProps:{...props,qa:true},frame:f,output:`${q}/frames/${loc}-${f}.png`,onBrowserLog:l=>{const k=l.text.indexOf('FILM_V13_AUDIT:');if(k>=0)rows.push(JSON.parse(l.text.slice(k+15)));}});
 writeFileSync(`${q}/${loc}-layout.json`,JSON.stringify(rows,null,2));
 const output=`${q}/${loc}-picture.mp4`;if(existsSync(output))throw Error('Refuse overwrite '+output);let last=-1;
 await renderMedia({...opts,composition:comp,inputProps:props,outputLocation:output,codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:94,concurrency:5,onProgress:({progress})=>{const n=Math.floor(progress*10)*10;if(n!==last){last=n;console.log(loc,n+'%')}}});
}}finally{await browser.close({silent:true})}
