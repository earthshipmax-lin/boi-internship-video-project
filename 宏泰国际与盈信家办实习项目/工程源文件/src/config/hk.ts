import voiceTimings from './vo-hk-timing.json';
export type SceneId='S0'|'S1'|'S2'|'S3'|'S4'|'S5'|'S6'|'S7';
export type SceneSpec={id:SceneId;start:number;end:number;title:string[];vo?:string;voiceover?:string;subtitleChunks?:string[];footage?:string;placeholder?:string;review?:string;cueOffsets?:number[]};
export const hk={
  voice:{locale:'yue-HK',script:'zh-Hant-HK',provider:'MiniMax speech-2.8-hd Gentle Lady',purpose:'natural-paced expressive preview'},voiceTimings,
  composition:'BOI-HK-MiniMax-v4',fps:30,width:1920,height:1080,duration:75.1,chineseOnly:false,
  logoTimeline:{baseStart:1.2,baseDur:.9,trunkStart:2,trunkDur:1.2,leavesStart:3,ringGap:.55,leafDur:.5,wordStart:7.4,wordDur:1,outStart:10.2,outDur:1.8,end:12},
  labels:{noVoice:'無配音',footagePrefix:'人工智能影片佔位：',quarter:['第一季','第二季','第三至四季'],wordmark:'宏泰國際'},
  subtitle:{leadIn:.35,tail:.3,fontSize:32},
  music:{file:'music/bgm.wav',volume:.16,duckVolume:.045,fadeIn:.8,fadeOut:1},
  scenes:[
    {id:'S0',start:0,end:12,title:['宏泰國際']},
    {id:'S1',start:12.0,end:19.2,title:['全球最大','跨境財富管理中心'],vo:'vo/hk-v4/VO-01.wav',voiceover:'香港，已成為全球最大的跨境財富管理中心。',subtitleChunks:["香港，", "已成為全球最大的跨境財富管理中心。"],footage:'footage/S1.mp4',placeholder:'清晨維港遠景（無可辨識人物），緩慢推鏡',review:'[待確認：數據口徑與出處]'},
    {id:'S2',start:19.2,end:26.6,title:['值得信任的人'],vo:'vo/hk-v4/VO-02.wav',voiceover:'市場越大，客戶越需要一位值得信任的人。',subtitleChunks:["市場越大，", "客戶越需要一位，", "值得信任的人。"],footage:'footage/S2.mp4',placeholder:'桌面上兩杯茶、一份文件的靜物特寫，不出現人臉'},
    {id:'S3',start:26.6,end:36.6,title:['信任，','是一圈一圈長出來的。'],vo:'vo/hk-v4/VO-03.wav',voiceover:'信任，不會一夜之間建立。它像橡樹的年輪，一圈一圈，慢慢長出來。',subtitleChunks:["信任，", "不會一夜之間建立。", "它像橡樹的年輪，", "一圈一圈，", "慢慢長出來。"]},
    {id:'S4',start:36.6,end:47.6,title:['合規','導師','系統'],vo:'vo/hk-v4/VO-04.wav',voiceover:'在宏泰國際，嚴謹的合規、資深的導師、專業的系統，陪你走好每一步。',subtitleChunks:["在宏泰國際，", "嚴謹的合規、", "資深的導師、", "專業的系統，", "陪你走好每一步。"],cueOffsets:[1,3.2,5.4]},
    {id:'S5',start:47.6,end:52.6,title:['立足香港'],vo:'vo/hk-v4/VO-05.wav',voiceover:'立足香港，紮根這片土地。',subtitleChunks:["立足香港，", "紮根這片土地。"]},
    {id:'S6',start:52.6,end:65.6,title:['專業根基','客戶網絡','獨當一面'],vo:'vo/hk-v4/VO-06.wav',voiceover:'第一季，打好專業根基。第二季，建立你的客戶網絡。第三、四季，成為獨當一面的理財顧問。',subtitleChunks:["第一季，", "打好專業根基。", "第二季，", "建立你的客戶網絡。", "第三、四季，", "成為獨當一面的理財顧問。"],cueOffsets:[.2,2.5,4.8]},
    {id:'S7',start:65.6,end:75.1,title:['歡迎加入宏泰大家庭'],vo:'vo/hk-v4/VO-07.wav',voiceover:'你的第一圈年輪，由今天開始。歡迎加入宏泰大家庭。',subtitleChunks:["你的第一圈年輪，", "由今天開始。", "歡迎加入宏泰大家庭。"]},
  ] as SceneSpec[],
} as const;
