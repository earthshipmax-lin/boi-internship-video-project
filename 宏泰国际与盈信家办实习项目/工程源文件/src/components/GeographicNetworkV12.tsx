import React from 'react';
import data from '../assets/world-v12.json';
const ease=(x:number)=>1-Math.pow(1-Math.max(0,Math.min(1,x)),3);
const points=(p:number[][])=>'M'+p.map(x=>x.join(' ')).join(' L');
const arrival:Record<string,number>={'香港':31.28,'深圳':32.06,'紐約':32.42,'新加坡':33.50};
const duration:Record<string,number>={'深圳':.32,'紐約':.86,'新加坡':.70};
export const GeographicNetworkV12:React.FC<{time:number;sceneTime:number}>=({time,sceneTime})=>{
 const visible=ease(sceneTime/1.0);const city=data.cities;const hk=city['香港'].xy;
 const regional=(lon:number,lat:number)=>[195+(lon-113.7)/.85*340,750+(.8-(lat-22))/ .8*150];
 const hr=regional(city['香港'].lon,city['香港'].lat),sr=regional(city['深圳'].lon,city['深圳'].lat);
 return <svg width={1920} height={1080} style={{position:'absolute',inset:0,opacity:visible}}>
  <defs><filter id="route-glow-v12"><feGaussianBlur stdDeviation="3"/></filter></defs>
  <g>{data.land_paths.map((d,i)=><path key={i} d={d} fill="#24556B" fillOpacity=".66" stroke="#4D8CA4" strokeWidth=".75" strokeOpacity=".5"/>)}</g>
  <g opacity=".12" stroke="#9CC8D7" strokeWidth=".8">
   {[-30,0,30,60].map(lat=><path key={lat} d={`M140 ${320+(80-lat)*4.4} H1780`}/>)}
   {[0,60,120,180,240,300].map(lon=><path key={lon} d={`M${140+(lon+40)/360*1640} 320 V892`}/>)}
  </g>
  {Object.entries(data.routes).map(([name,coords])=>{const p=ease((time-arrival[name])/duration[name]);const idx=Math.min(99,Math.floor(p*100));const pos=coords[idx];return <g key={name} opacity={time>=arrival[name]?1:0}>
   <path d={points(coords)} fill="none" stroke="#8DD8F4" strokeWidth="6" opacity=".28" filter="url(#route-glow-v12)" pathLength="1" strokeDasharray="1" strokeDashoffset={1-p}/>
   <path d={points(coords)} fill="none" stroke={name==='新加坡'?'#B9C7CB':'#D7F1FC'} strokeWidth={name==='深圳'?2:2.2} pathLength="1" strokeDasharray="1" strokeDashoffset={1-p}/>
   {p<1&&<circle cx={pos[0]} cy={pos[1]} r="4.5" fill="#F4EEE2"/>}
  </g>;})}
  {Object.entries(city).map(([name,c])=>{const p=ease((time-arrival[name])/.3);const [x,y]=c.xy;const label:Record<string,[number,number]>={'香港':[-95,52],'深圳':[42,-35],'紐約':[18,-25],'新加坡':[28,44]};const [dx,dy]=label[name];return <g key={name} opacity={p}>
   <circle cx={x} cy={y} r={name==='香港'?7:5} fill="#F4EEE2"/>
   <circle cx={x} cy={y} r={name==='香港'?17:12} fill="none" stroke="#D7F1FC" strokeWidth="1" opacity=".6"/>
   {name!=='紐約'&&<path d={`M${x} ${y} L${x+dx*.75} ${y+dy*.7}`} fill="none" stroke="#C4E9F5" opacity=".6"/>}
   <text x={x+dx} y={y+dy} fill="#F4EEE2" fontFamily="Noto Sans TC" fontSize="33" fontWeight="700">{name}</text>
   {name==='新加坡'&&<text x={x+dx} y={y+dy+30} fill="#BBCDD5" fontFamily="Noto Sans TC" fontSize="21">籌備中</text>}
  </g>;})}
  <g opacity={ease((time-31.28)/.4)}>
   <path d={`M${hk[0]} ${hk[1]} Q670 650 580 755`} fill="none" stroke="#89AEBE" strokeDasharray="3 6" opacity=".4"/>
   <rect x="150" y="736" width="430" height="180" rx="2" fill="#0B2E45" fillOpacity=".9" stroke="#416F84" strokeWidth="1"/>
   <text x="175" y="765" fill="#B8D1DC" fontSize="18" fontFamily="Noto Sans TC" letterSpacing="2">香港—深圳 · 局部放大</text>
   <path d={`M${hr[0]} ${hr[1]} L${sr[0]} ${sr[1]}`} fill="none" stroke="#D7F1FC" strokeWidth="2" pathLength="1" strokeDasharray="1" strokeDashoffset={1-ease((time-32.06)/.32)}/>
   <circle cx={hr[0]} cy={hr[1]} r="5" fill="#F4EEE2"/><text x={hr[0]+16} y={hr[1]+8} fontSize="25" fontFamily="Noto Sans TC" fill="#F4EEE2">香港</text>
   <g opacity={ease((time-32.06)/.2)}><circle cx={sr[0]} cy={sr[1]} r="5" fill="#F4EEE2"/><text x={sr[0]-70} y={sr[1]-8} fontSize="25" fontFamily="Noto Sans TC" fill="#F4EEE2">深圳</text></g>
  </g>
 </svg>;
};
