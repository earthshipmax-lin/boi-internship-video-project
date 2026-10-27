import {useEffect,useState} from 'react';
import {getStaticFiles,getRemotionEnvironment,staticFile,delayRender,continueRender,cancelRender} from 'remotion';
import {hk} from './config/hk';
export type MediaAssets=Record<string,{duration:number}>;
const durations=new Map<string,Promise<number>>();
// Explicit load and shared promises avoid duplicate metadata loads in separate
// scene/caption/audio tracks and browsers whose default preload is "none".
const readDuration=(file:string)=>{
 const url=staticFile(file);const existing=durations.get(url);if(existing)return existing;
 const promise=new Promise<number>((resolve,reject)=>{
  const media=document.createElement(/\.mp4$/i.test(file)?'video':'audio');
  media.preload='auto';media.muted=true;
  const timer=setTimeout(()=>fail(new Error(`Timed out reading local media duration: ${file}`)),15000);
  const cleanup=()=>{clearTimeout(timer);media.removeEventListener('loadedmetadata',done);media.removeEventListener('error',onError);media.removeAttribute('src');media.load();media.remove();};
  const fail=(error:Error)=>{cleanup();durations.delete(url);reject(error);};
  const onError=()=>fail(new Error(`Cannot decode local media: ${file}`));
  const done=()=>{const seconds=media.duration;if(!Number.isFinite(seconds)||seconds<=0){fail(new Error(`Invalid local media duration: ${file}`));return;}cleanup();resolve(seconds);};
  media.addEventListener('loadedmetadata',done,{once:true});media.addEventListener('error',onError,{once:true});media.src=url;media.load();
 });
 durations.set(url,promise);return promise;
};
let playerAssetsPromise:Promise<MediaAssets>|undefined;
const readPlayerAssets=()=>{
 if(playerAssetsPromise)return playerAssetsPromise;
 const candidates=[...new Set([...hk.scenes.flatMap(s=>[s.vo,s.footage]),hk.music.file].filter((s):s is string=>Boolean(s)))];
 playerAssetsPromise=Promise.all(candidates.map(async name=>{
  const response=await fetch(staticFile(name),{method:'HEAD',cache:'no-store'});
  // Vite's SPA fallback returns HTML for missing files; it is not a real asset.
  if(!response.ok||!/(audio|video)\//i.test(response.headers.get('content-type')??''))return null;
  return [name,{duration:await readDuration(name)}] as const;
 })).then(entries=>Object.fromEntries(entries.filter((e):e is NonNullable<typeof e>=>e!==null)));
 return playerAssetsPromise;
};
export const useMediaAssets=()=>{
 const player=getRemotionEnvironment().isPlayer;
 const files=player?[]:getStaticFiles();const key=files.map(f=>`${f.name}:${f.sizeInBytes}:${f.lastModified}`).join('|');
 const [handle]=useState(()=>delayRender('Check local footage and voice duration'));
 const [assets,setAssets]=useState<MediaAssets>({});
 useEffect(()=>{
  let live=true;
  const loading=player?readPlayerAssets():Promise.all(files.filter(f=>/\.(wav|mp3|mp4)$/i.test(f.name)).map(async f=>[f.name,{duration:await readDuration(f.name)}] as const)).then(entries=>Object.fromEntries(entries));
  loading.then(value=>{if(live){setAssets(value);continueRender(handle);}}).catch(cancelRender);
  return ()=>{live=false;};
 },[key,handle,player]);
 return assets;
};
