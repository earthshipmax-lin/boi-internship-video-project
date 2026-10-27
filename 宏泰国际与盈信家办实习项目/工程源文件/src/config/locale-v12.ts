import originalCaptions from './captions-v12-stage3.json';

/** Text preparation only. No Scene, recording, timing extension or global
 * language state is introduced by importing this module. */
export type Locale='yue'|'en'|'zh-CN';
export type LocalizedText=Readonly<Record<Locale,string>>;
export const localesV12=['yue','en','zh-CN'] as const;
export const localeFontsV12={yue:'Noto Sans TC',en:'Geist','zh-CN':'Noto Sans TC'} as const;
export const localePreparationV12={scope:'shared_text_configuration_only',status:'prepared_not_integrated',
  sources:['CODEX_PROMPT_13_多語言與地圖重做.md','CODEX_PROMPT_14_人物展示與加長版.md'],
  existingCaptionSource:'src/config/captions-v12-stage3.json',newNarrationTiming:null} as const;

// Prompt13's unique translation table. Cantonese strings are the existing
// source verbatim. Only the table's mixed-script CN typo 未來 -> 未来 is fixed.
const captionTextV12=[
  {yue:'一個家族嘅未來','zh-CN':'一个家族的未来',en:"A family's future"},
  {yue:'值得我哋睇得更遠','zh-CN':'值得看得更远',en:'Worth a longer view'},
  {yue:'源自一九九七年','zh-CN':'源自一九九七年',en:'Since 1997'},
  {yue:'我哋一路走來，靠嘅係專業','zh-CN':'我们一路走来，靠的是专业',en:'Built on expertise, every step of the way'},
  {yue:'更加係每一份交到手上嘅信任','zh-CN':'更是每一份交到手上的信任',en:'And on every trust placed in our hands'},
  {yue:'集團總保費超過一百億港元','zh-CN':'集团总保费超过一百亿港元',en:'Over HK$10 billion in total premiums'},
  {yue:'總佣金超過十五億港元','zh-CN':'总佣金超过十五亿港元',en:'Over HK$1.5 billion in total commission'},
  {yue:'服務超過兩萬位高淨值客戶','zh-CN':'服务超过两万位高净值客户',en:'Serving over 20,000 high-net-worth clients'},
  {yue:'每一個數字背後','zh-CN':'每一个数字背后',en:'Behind every figure'},
  {yue:'都有一個家庭，對未來嘅期望','zh-CN':'都有一个家庭，对未来的期望',en:"A family's hope for the future"},
  {yue:'所以，我哋一直向前','zh-CN':'所以，我们一直向前',en:'So we keep moving forward'},
  {yue:'連繫香港、深圳、紐約','zh-CN':'联系香港、深圳、纽约',en:'Connecting Hong Kong, Shenzhen, New York'},
  {yue:'新加坡亦正籌備中','zh-CN':'新加坡亦正筹备中',en:'Singapore in preparation'},
  {yue:'從保險、信託，到稅務','zh-CN':'从保险、信托，到税务',en:'From insurance and trusts to tax'},
  {yue:'教育同身份規劃','zh-CN':'教育与身份规划',en:'Education and residency planning'},
  {yue:'將專業連成一個平台','zh-CN':'将专业连成一个平台',en:'One platform, built on expertise'},
  {yue:'為每一個家族','zh-CN':'为每一个家族',en:'For every family'},
  {yue:'睇得更全面，行得更長遠','zh-CN':'看得更全面，行得更长远',en:'A fuller view. A longer road.'},
  {yue:'眼光，可以跨越地域','zh-CN':'眼光，可以跨越地域',en:'Vision crosses borders'},
  {yue:'信任，需要時間扎根','zh-CN':'信任，需要时间扎根',en:'Trust takes root in time'},
  {yue:'根扎得深，先可以長得更高','zh-CN':'根扎得深，才可以长得更高',en:'Deep roots reach higher'},
  {yue:'步伐夠穩，先可以走得更遠','zh-CN':'步伐够稳，才可以走得更远',en:'Steady steps go further'},
  {yue:'大展宏圖，穩如泰山','zh-CN':'大展宏图，稳如泰山',en:'Grand vision. Steady as a mountain.'},
  {yue:'宏泰國際','zh-CN':'宏泰国际',en:'Blue Oak International'},
] as const satisfies readonly LocalizedText[];

export type CaptionCueV12=Readonly<{id:string;start:number;end:number;text:LocalizedText}>;
if(originalCaptions.length!==captionTextV12.length)throw new Error('Locale preparation: original caption count changed; review translations.');
export const captionCuesV12:readonly CaptionCueV12[]=originalCaptions.map((cue,index)=>{
  const text=captionTextV12[index];
  if(cue.text!==text.yue)throw new Error(`Locale preparation: original Cantonese cue ${index+1} changed; review rather than rewrite.`);
  return {id:`caption-${String(index+1).padStart(2,'0')}`,start:cue.start,end:cue.end,text};
});
export type RenderCaptionV12=Readonly<{id:string;start:number;end:number;text:string}>;
export const getCaptionsV12=(locale:Locale):readonly RenderCaptionV12[]=>captionCuesV12.map(cue=>({id:cue.id,start:cue.start,end:cue.end,text:cue.text[locale]}));
export const captionsV12ByLocale:Readonly<Record<Locale,readonly RenderCaptionV12[]>>={
  yue:getCaptionsV12('yue'),en:getCaptionsV12('en'),'zh-CN':getCaptionsV12('zh-CN'),
};
export const getCaptionAtV12=(locale:Locale,time:number):RenderCaptionV12|null=>
  captionsV12ByLocale[locale].find(cue=>time>=cue.start&&time<cue.end+.12)??null;

/** Only exact table-backed screen phrases are included. Existing headlines
 * with different Cantonese wording remain in the inventory below. */
export const screenTextV12={
  visionTitle:{yue:'看得更遠。','zh-CN':'看得更远。',en:'See Further.'},
  visionSubtitle:{yue:'未來，值得更長遠的眼光','zh-CN':'未来，值得更长远的眼光',en:'The future deserves a longer view'},
  awardsTitle:{yue:'每一份信任，都有分量。','zh-CN':'每一份信任，都有分量。',en:'Every trust carries weight.'},
  awardsSubtitle:{yue:'業界肯定，見證專業積累','zh-CN':'业界肯定，见证专业积累',en:'Recognised across the industry'},
  platformTitle:{yue:'一個平台，連繫未來。','zh-CN':'一个平台，联系未来。',en:'One platform, connecting the future.'},
  valuesMeta:{yue:'專業為本 · 穩健為根','zh-CN':'专业为本 · 稳健为根',en:'Expertise first. Stability always.'},
  invitation:{yue:'宏泰國際 · 誠邀出席','zh-CN':'宏泰国际 · 诚邀出席',en:'An invitation from Blue Oak'},
  watermark:{yue:'內部審片版 · 不作對外發布','zh-CN':'内部审片版 · 不作对外发布',en:'INTERNAL REVIEW COPY — NOT FOR DISTRIBUTION'},
  peopleTitle:{yue:'專業，由人而來','zh-CN':'专业，由人而来',en:'Expertise, by people'},
  brandName:{yue:'宏泰國際','zh-CN':'宏泰国际',en:'Blue Oak International'},
} as const satisfies Readonly<Record<string,LocalizedText>>;
export type ScreenTextKeyV12=keyof typeof screenTextV12;
export const getScreenTextV12=(locale:Locale,key:ScreenTextKeyV12):string=>screenTextV12[key][locale];

// Geographic spellings are already present in Prompt13's city sentence and
// the current office assets' English names; no new addresses are translated.
export const locationLabelsV12={
  hk:{yue:'香港','zh-CN':'香港',en:'Hong Kong'},
  sz:{yue:'深圳','zh-CN':'深圳',en:'Shenzhen'},
  ny:{yue:'紐約','zh-CN':'纽约',en:'New York'},
  sg:{yue:'新加坡','zh-CN':'新加坡',en:'Singapore'},
} as const satisfies Readonly<Record<string,LocalizedText>>;
export const brandAssetLanguageExceptionsV12=[
  {kind:'official_logo',note:'Original brand artwork and its BLUE OAK INTERNATIONAL wordmark remain unchanged.'},
  {kind:'source_photo_or_certificate',note:'Embedded signs, portraits and certificate lettering are original source pixels, not locale-generated screen copy.'},
] as const;

/** Prompt14 unique narration table, six rows verbatim. No durations or cue
 * positions are guessed before sample generation and audition. */
export const peopleNarrationV13=[
  {id:'opening',subjects:[],text:{yue:'平台嘅高度，由人嚟決定。','zh-CN':'平台的高度，由人来决定。',en:'A platform rises as high as its people.'}},
  {id:'david-lau',subjects:['david-lau'],text:{yue:'三十年跨國企業經驗，帶領集團看得更遠。','zh-CN':'三十年跨国企业经验，带领集团看得更远。',en:'Thirty years with global firms, leading the group to see further.'}},
  {id:'patrick-li',subjects:['patrick-li'],text:{yue:'精算嘅嚴謹，令每一份方案經得起時間。','zh-CN':'精算的严谨，让每一份方案经得起时间。',en:'Actuarial rigour that lets every plan stand the test of time.'}},
  {id:'operations-compliance',subjects:['pamela-cheng','manli-chan'],text:{yue:'由營運到合規，每一個環節，都有人把關。','zh-CN':'从营运到合规，每一个环节，都有人把关。',en:'From operations to compliance, every step has a guardian.'}},
  {id:'hong-kong-new-york',subjects:['ken-yeung','david-wang'],text:{yue:'由香港到紐約，同一份專業，同一份承諾。','zh-CN':'从香港到纽约，同一份专业，同一份承诺。',en:'From Hong Kong to New York, one standard, one promise.'}},
  {id:'partner-wall',subjects:['lily-ku','noah-cheung','catherine-luo','vivian-mau','crystal-wang'],text:{yue:'一群人，一個方向：守護每一個家族嘅未來。','zh-CN':'一群人，一个方向：守护每一个家族的未来。',en:"Many people, one purpose: safeguarding every family's future."}},
] as const satisfies readonly Readonly<{id:string;subjects:readonly string[];text:LocalizedText}>[];
export type PeopleNarrationIdV13=typeof peopleNarrationV13[number]['id'];
export const getPeopleNarrationV13=(locale:Locale,id:PeopleNarrationIdV13):string=>peopleNarrationV13.find(row=>row.id===id)!.text[locale];

export type PlannedVoiceSampleV13=Readonly<{
  id:string;locale:Locale;narrationId:PeopleNarrationIdV13;text:string;requestedSpeed:number;
  status:'planned';generationStatus:'not_generated';requiresAuditionBeforeRemainingGeneration:true;
  tool:null;model:null;voiceId:null;durationSeconds:null;generatedAt:null;audioFile:null;actualSpeed:null;
  plannedOutput:string;voiceReference:string;
}>;
const samplePlan=(id:string,locale:Locale,narrationId:PeopleNarrationIdV13,requestedSpeed:number,folder:string):PlannedVoiceSampleV13=>({
  id,locale,narrationId,text:getPeopleNarrationV13(locale,narrationId),requestedSpeed,
  status:'planned',generationStatus:'not_generated',requiresAuditionBeforeRemainingGeneration:true,
  tool:null,model:null,voiceId:null,durationSeconds:null,generatedAt:null,audioFile:null,actualSpeed:null,
  plannedOutput:`vo/hk-v13/${folder}/people-${narrationId}.mp3`,voiceReference:'qa/v11/voice-r06/provenance.json',
});
/** Historical pre-generation plan. Actual generated samples, measured durations and
 * approval status are authoritative in public/vo/hk-v13/VOICE_PROVENANCE.json. */
export const plannedVoiceSamplesV13:readonly PlannedVoiceSampleV13[]=[
  samplePlan('yue-opening','yue','opening',1,'yue'),
  samplePlan('yue-david-lau','yue','david-lau',1,'yue'),
  samplePlan('en-opening','en','opening',1.05,'en'),
  samplePlan('cn-opening','zh-CN','opening',1.05,'cn'),
];
export const existingVoiceReferenceV12={
  voiceDisplayName:'BOI-v11-Cinematic-r05-test',verifiedApiVoiceId:null,
  verifiedUiVoiceId:'ttv-voice-2026102209482426-zCcLsM7s',voiceIdEvidence:'MiniMax visible Copy voice ID control/tooltip, 2026-10-26',
  body:{source:'qa/v11/voice-r06/full-source.mp3',provenance:'qa/v11/voice-r06/provenance.json',generationSpeed:1},
  ending:{source:'qa/v12/ending-source-r02.mp3',provenance:'qa/v12/voice-provenance.json',generationSpeed:.92},
  retainedMix:'music/v12-stage3/review-mix.wav',
  auditionReference:{description:'Existing S1 clean voice excerpt; safe silence endpoint verified for the audition derivative only.',source:'qa/v12/stage3/voice-timeline.wav',startSeconds:2.1,endSeconds:6.04},
} as const;

/** Historical inventory of the38 UI gaps at initial preparation. Current
 * table coverage is in screen-copy-v13.ts; full-scene integration/fit is pending.
 * Neither module supplies Chinese fallback for the English Scene. */
export const untranslatedInventoryV12=[
  {id:'meta.vision',source:'每一個家族的未來',context:'Opening corner meta'},
  {id:'meta.origin',source:'時間 · 專業 · 信任',context:'Origin corner meta'},
  {id:'meta.premium',source:'01 / 集團實力',context:'Premium corner meta'},
  {id:'meta.commission',source:'02 / 集團實力',context:'Commission corner meta'},
  {id:'meta.clients',source:'03 / 集團實力',context:'Clients corner meta'},
  {id:'meta.awards',source:'專業的積累',context:'Awards corner meta'},
  {id:'meta.map',source:'全球視野 · 一路向前',context:'Map corner meta'},
  {id:'meta.platform',source:'家族辦公室平台',context:'Platform corner meta'},
  {id:'meta.offices',source:'三城辦公室 · 公司實景',context:'Office corner meta'},
  {id:'meta.roots',source:'根深 · 步穩 · 向前',context:'Roots corner meta'},
  {id:'origin.label',source:'集團源自',context:'Origin label'},
  {id:'origin.year',source:'1997年',context:'Year label typography and unit'},
  {id:'origin.support',source:'一路走來，承接每一份信任。',context:'Origin support line'},
  {id:'premium.label',source:'集團總保費',context:'Numeric scene label'},
  {id:'commission.label',source:'集團總佣金',context:'Numeric scene label'},
  {id:'data.values',source:'100億+ / 15億+ / 2萬+',context:'Localized numeral units; amount facts remain unchanged'},
  {id:'data.currency',source:'港元',context:'Currency label'},
  {id:'clients.label',source:'高淨值客戶',context:'Clients label'},
  {id:'clients.support',source:'數字背後，是信任。',context:'Clients support line'},
  {id:'map.title',source:'讓眼光，跨越地域。',context:'Actual main map headline differs from caption table'},
  {id:'map.singapore-status',source:'籌備中',context:'Standalone status badge; full translated sentence exists only as a caption'},
  {id:'map.regional-title',source:'香港 — 深圳 · 12×',context:'Prompt13 map title; actual multiplier unresolved, do not promise 12×'},
  {id:'offices.headline',source:'看得全面。行得長遠。',context:'Actual office headline differs from caption table'},
  {id:'offices.vision-title',source:'眼光，跨越地域。',context:'Independent vision-page headline'},
  {id:'offices.hk-address',source:'尖沙咀 · 新港中心',context:'Office building-level address'},
  {id:'offices.sz-address',source:'南山 · 康泰創新廣場',context:'Office building-level address'},
  {id:'offices.ny-address',source:'Flushing · New York',context:'Current office address spelling needs CN display decision'},
  {id:'values.title',source:'信任，扎根時間。',context:'Independent trust headline differs from caption table'},
  {id:'roots.title',source:'根扎得深，\n長得更高。',context:'Actual two-line roots title differs from caption table'},
  {id:'platform.sectors',source:'核心保險業務 / 家族辦公室 / 財富管理',context:'Three sector titles'},
  {id:'platform.nodes',source:'保險 / 信託 / 稅務 / 教育 / 身份',context:'Five node labels'},
  {id:'platform.insurance-evidence',source:'香港 · 澳門 · 美國 / 百慕達 · 新加坡',context:'Sector geographical evidence'},
  {id:'platform.wealth-evidence',source:'信託 · 遺產 / 稅務規劃',context:'Wealth evidence'},
  {id:'platform.family-evidence',source:'盈信家辦 EVERGREEN',context:'Family evidence; official artwork retained separately'},
  {id:'legal.licences',source:'保監局持牌 FB1681 · PIBA會員 M0573',context:'Licence/association footer'},
  {id:'legal.compliance',source:'全面風險管理 · 合規操作準則 · 客戶隱私保護 · 業務持續運營',context:'Four compliance statements'},
  {id:'awards.couplet-labels',source:'永明金融 SUN LIFE / 友邦 AIA',context:'Prompt13 labels; identities require PDF page5 evidence'},
  {id:'people.names-roles-merits',source:'六位主角姓名／職銜／功績及五位合夥人姓名／職銜',context:'Prompt14 authorizes PDF-based translation but gives no complete unique translated table; pending verified people content config'},
] as const;
export const untranslatedPolicyV12={missingLocales:['en','zh-CN'],status:'requires_table_completion_or_explicit_translation_review',
  fallback:null,mayInventFacts:false,maySilentlyRewriteApprovedCaption:false} as const;
